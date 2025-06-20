"""
MCP Database Integration for Hospital AI Helper
Provides intelligent database query capabilities using Model Context Protocol
"""

import re
import json
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from pathlib import Path
import sys

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor

    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    logging.warning("psycopg2 not available. Database integration disabled.")

from config.secure_config import load_database_config, get_connection_string
from .db_pool import get_db_connection

logger = logging.getLogger(__name__)


@dataclass
class QueryResult:
    """Structure for database query results"""

    success: bool
    data: List[Dict[str, Any]]
    query: str
    row_count: int
    error_message: Optional[str] = None


@dataclass
class QueryIntent:
    """Structure for parsed user query intent"""

    intent_type: str  # 'patient_lookup', 'room_status', 'equipment', 'occupancy', etc.
    entities: Dict[str, Any]  # Extracted entities like names, room numbers, etc.
    confidence: float
    suggested_tables: List[str]


class DatabaseMCP:
    """
    Model Context Protocol Database Integration
    Intelligently maps user queries to database operations
    """

    def __init__(self):
        """Initialize the MCP database service"""
        self.db_config = None
        self.schema_info = {}
        self._initialize_connection()

    def _initialize_connection(self):
        """Initialize database connection"""
        if not DB_AVAILABLE:
            logger.error("Database libraries not available")
            return

        try:
            self.db_config = load_database_config()
            logger.info("Database configuration loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load database configuration: {e}")

    def parse_user_intent(self, user_query: str) -> QueryIntent:
        """
        Parse user query to understand intent and extract entities
        """
        user_query_lower = user_query.lower()

        # Intent patterns
        intent_patterns = {
            "patient_lookup": [
                r"patient.*(?:named?|called)\s+(\w+)",
                r"find.*patient.*(\w+)",
                r"(?:who is|show me).*patient.*(\w+)",
                r"medical record.*for.*(\w+)",
                r"patient.*(\w+).*(?:information|details|record)",
            ],
            "room_status": [
                r"room\s+([A-Z]?\d+)",
                r"show.*me.*room\s+([A-Z]?\d+)",
                r"(?:what|which).*room.*(?:available|empty|occupied)",
                r"room.*(?:status|occupancy)",
                r"available.*rooms?",
                r"empty.*rooms?",
            ],
            "equipment_inventory": [
                r"(?:equipment|tools?).*(?:available|inventory)",
                r"(?:what|how many).*(?:equipment|tools?)",
                r"medical.*(?:equipment|tools?)",
                r"inventory.*(?:equipment|tools?)",
                r"(?:find|show).*(?:equipment|tools?)",
            ],
            "hospital_stats": [
                r"(?:how many|total).*patients?",
                r"(?:hospital|statistics|stats)",
                r"occupancy.*rate",
                r"total.*(?:rooms?|beds?)",
                r"hospital.*(?:capacity|overview)",
            ],
            "staff_lookup": [
                r"staff.*(?:named?|called)\s+(\w+)",
                r"(?:doctor|nurse|staff).*(\w+)",
                r"find.*(?:doctor|nurse|staff).*(\w+)",
            ],
        }

        # Find matching intent
        best_intent = "general_query"
        entities = {}
        confidence = 0.5

        for intent_type, patterns in intent_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, user_query_lower)
                if match:
                    best_intent = intent_type
                    confidence = 0.8
                    if match.groups():
                        entities["search_term"] = match.group(1)
                    break
            if confidence > 0.7:
                break

        # Determine suggested tables based on intent
        table_mapping = {
            "patient_lookup": ["users", "patient_records"],
            "room_status": ["rooms", "occupancy"],
            "equipment_inventory": ["tools", "hospital_inventory", "storage_rooms"],
            "hospital_stats": ["users", "rooms", "occupancy", "patient_records"],
            "staff_lookup": ["users"],
        }

        suggested_tables = table_mapping.get(best_intent, ["users"])

        return QueryIntent(
            intent_type=best_intent,
            entities=entities,
            confidence=confidence,
            suggested_tables=suggested_tables,
        )

    def generate_sql_query(self, intent: QueryIntent) -> str:
        """
        Generate SQL query based on parsed intent
        """
        if intent.intent_type == "patient_lookup":
            if "search_term" in intent.entities:
                return f"""
                SELECT u.id, u.full_name, u.role, pr.date_of_birth, pr.gender, 
                       pr.blood_group, pr.medical_history, pr.allergies
                FROM users u
                LEFT JOIN patient_records pr ON u.id = pr.user_id
                WHERE LOWER(u.full_name) LIKE '%{intent.entities['search_term']}%'
                AND u.role = 'patient'
                LIMIT 10
                """
            else:
                return """
                SELECT u.id, u.full_name, pr.date_of_birth, pr.gender, pr.blood_group
                FROM users u
                LEFT JOIN patient_records pr ON u.id = pr.user_id
                WHERE u.role = 'patient'
                LIMIT 10
                """

        elif intent.intent_type == "room_status":
            if "search_term" in intent.entities:
                return f"""
                SELECT r.room_number, r.room_type, r.bed_capacity, 
                       CASE 
                           WHEN o.id IS NOT NULL AND o.discharged_at IS NULL THEN 'Occupied'
                           ELSE 'Available'
                       END as status,
                       u.full_name as patient_name,
                       o.assigned_at
                FROM rooms r
                LEFT JOIN occupancy o ON r.id = o.room_id AND o.discharged_at IS NULL
                LEFT JOIN patient_records pr ON o.patient_id = pr.id
                LEFT JOIN users u ON pr.user_id = u.id
                WHERE r.room_number = '{intent.entities['search_term'].upper()}'
                """
            else:
                return """
                SELECT r.room_number, r.room_type, r.bed_capacity,
                       CASE 
                           WHEN o.id IS NOT NULL AND o.discharged_at IS NULL THEN 'Occupied'
                           ELSE 'Available'
                       END as status
                FROM rooms r
                LEFT JOIN occupancy o ON r.id = o.room_id AND o.discharged_at IS NULL
                ORDER BY r.room_number
                LIMIT 20
                """

        elif intent.intent_type == "equipment_inventory":
            return """
            SELECT t.tool_name, t.category, t.quantity_total, t.quantity_available,
                   sr.storage_number, sr.storage_type
            FROM tools t
            LEFT JOIN storage_rooms sr ON t.location_storage_id = sr.id
            WHERE t.quantity_available > 0
            ORDER BY t.category, t.tool_name
            LIMIT 20
            """

        elif intent.intent_type == "hospital_stats":
            return """
            SELECT 
                'Total Patients' as metric,
                COUNT(*) as value
            FROM users WHERE role = 'patient'
            UNION ALL
            SELECT 
                'Total Rooms' as metric,
                COUNT(*) as value
            FROM rooms
            UNION ALL
            SELECT 
                'Occupied Rooms' as metric,
                COUNT(*) as value
            FROM occupancy WHERE discharged_at IS NULL
            UNION ALL
            SELECT 
                'Available Equipment' as metric,
                SUM(quantity_available) as value
            FROM tools
            """

        elif intent.intent_type == "staff_lookup":
            if "search_term" in intent.entities:
                return f"""
                SELECT id, full_name, role, staff_type, email
                FROM users
                WHERE role IN ('staff', 'admin')
                AND LOWER(full_name) LIKE '%{intent.entities['search_term']}%'
                LIMIT 10
                """
            else:
                return """
                SELECT id, full_name, role, staff_type
                FROM users
                WHERE role IN ('staff', 'admin')
                LIMIT 10
                """        # Default general query
        return """
        SELECT 'Hospital Overview' as info,
               'Use more specific queries like: patient John, room R001, available equipment, hospital stats' as suggestion
        """

    def execute_query(self, sql_query: str) -> QueryResult:
        """
        Execute SQL query and return structured results
        """
        try:
            with get_db_connection() as connection:
                cursor = connection.cursor(cursor_factory=RealDictCursor)

                # Clean and validate query
                sql_query = sql_query.strip()
                if not sql_query.upper().startswith("SELECT"):
                    raise ValueError("Only SELECT queries are allowed")

                cursor.execute(sql_query)
                results = cursor.fetchall()

                # Convert to list of dictionaries
                data = [dict(row) for row in results]

                cursor.close()

                return QueryResult(
                    success=True, data=data, query=sql_query, row_count=len(data)
                )

        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return QueryResult(
                success=False,
                data=[],
                query=sql_query,
                row_count=0,
                error_message=str(e),
            )

    def format_response(self, query_result: QueryResult, intent: QueryIntent) -> str:
        """
        Format database results into a coherent, contextually appropriate response
        """
        if not query_result.success:
            return f"I encountered an error while searching the database: {query_result.error_message}"

        if query_result.row_count == 0:
            return "I couldn't find any matching information in the hospital database."

        data = query_result.data

        # Format based on intent type
        if intent.intent_type == "patient_lookup":
            if query_result.row_count == 1:
                patient = data[0]
                response = f"**Patient Information:**\n"
                response += f"• Name: {patient.get('full_name', 'N/A')}\n"
                response += f"• Date of Birth: {patient.get('date_of_birth', 'N/A')}\n"
                response += f"• Gender: {patient.get('gender', 'N/A')}\n"
                response += f"• Blood Group: {patient.get('blood_group', 'N/A')}\n"
                if patient.get("medical_history"):
                    response += f"• Medical History: {patient.get('medical_history')}\n"
                if patient.get("allergies"):
                    response += f"• Allergies: {patient.get('allergies')}\n"
            else:
                response = f"**Found {query_result.row_count} patients:**\n"
                for i, patient in enumerate(data[:5], 1):
                    response += f"{i}. {patient.get('full_name', 'N/A')} - {patient.get('blood_group', 'N/A')}\n"

        elif intent.intent_type == "room_status":
            if "search_term" in intent.entities:
                if data:
                    room = data[0]
                    response = f"**Room {room.get('room_number')} Status:**\n"
                    response += f"• Type: {room.get('room_type', 'N/A')}\n"
                    response += f"• Capacity: {room.get('bed_capacity', 'N/A')} beds\n"
                    response += f"• Status: {room.get('status', 'N/A')}\n"
                    if room.get("patient_name"):
                        response += f"• Current Patient: {room.get('patient_name')}\n"
                        response += f"• Admitted: {room.get('assigned_at', 'N/A')}\n"
                else:
                    response = (
                        f"Room {intent.entities['search_term'].upper()} not found."
                    )
            else:
                available_rooms = [r for r in data if r.get("status") == "Available"]
                occupied_rooms = [r for r in data if r.get("status") == "Occupied"]

                response = f"**Room Status Summary:**\n"
                response += f"• Available Rooms: {len(available_rooms)}\n"
                response += f"• Occupied Rooms: {len(occupied_rooms)}\n\n"

                if available_rooms:
                    response += "**Available Rooms:**\n"
                    for room in available_rooms[:5]:
                        response += (
                            f"• {room.get('room_number')} ({room.get('room_type')})\n"
                        )

        elif intent.intent_type == "equipment_inventory":
            response = (
                f"**Medical Equipment Inventory ({query_result.row_count} items):**\n"
            )
            by_category = {}
            for item in data:
                category = item.get("category", "Other")
                if category not in by_category:
                    by_category[category] = []
                by_category[category].append(item)

            for category, items in by_category.items():
                response += f"\n**{category}:**\n"
                for item in items[:3]:
                    response += f"• {item.get('tool_name', 'N/A')}: {item.get('quantity_available', 0)} available\n"

        elif intent.intent_type == "hospital_stats":
            response = "**Hospital Statistics:**\n"
            for stat in data:
                response += (
                    f"• {stat.get('metric', 'N/A')}: {stat.get('value', 'N/A')}\n"
                )

        elif intent.intent_type == "staff_lookup":
            response = f"**Staff Information ({query_result.row_count} found):**\n"
            for i, staff in enumerate(data[:5], 1):
                response += f"{i}. {staff.get('full_name', 'N/A')} - {staff.get('staff_type', staff.get('role', 'N/A'))}\n"

        else:
            # Generic formatting
            response = (
                f"**Database Results ({query_result.row_count} records found):**\n"
            )
            for i, record in enumerate(data[:5], 1):
                response += f"{i}. {dict(record)}\n"

        return response

    def process_user_query(self, user_query: str) -> str:
        """
        Main MCP function: Process user query and return intelligent response
        """
        try:
            # Step 1: Parse user intent
            intent = self.parse_user_intent(user_query)
            logger.info(
                f"Parsed intent: {intent.intent_type} (confidence: {intent.confidence})"
            )

            # Step 2: Generate SQL query
            sql_query = self.generate_sql_query(intent)
            logger.debug(f"Generated SQL: {sql_query}")

            # Step 3: Execute query
            result = self.execute_query(sql_query)

            # Step 4: Format response
            formatted_response = self.format_response(result, intent)

            return formatted_response

        except Exception as e:
            logger.error(f"MCP processing failed: {e}")
            return f"I'm sorry, I encountered an error while processing your request: {str(e)}"

    def is_database_query(self, user_query: str) -> bool:
        """
        Determine if a user query requires database information
        """
        database_keywords = [
            "patient",
            "room",
            "equipment",
            "staff",
            "doctor",
            "nurse",
            "medical",
            "hospital",
            "inventory",
            "occupancy",
            "available",
            "find",
            "show",
            "search",
            "how many",
            "total",
            "statistics",
            "record",
            "history",
            "allergies",
            "blood",
            "bed",
        ]

        user_query_lower = user_query.lower()
        return any(keyword in user_query_lower for keyword in database_keywords)


# Global instance
database_mcp = DatabaseMCP()
