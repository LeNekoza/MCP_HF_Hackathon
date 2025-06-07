"""
Advanced MCP Database Integration for Hospital AI Helper
Uses Gemini function calling to generate complex SQL queries including JOINs
Based on Google Cloud examples for SQL function calling with Gemini
"""

import re
import json
import logging
from typing import Dict, List, Optional, Any
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

try:
    import vertexai
    from vertexai.generative_models import (
        GenerativeModel,
        FunctionDeclaration,
        Tool,
        Content,
        Part,
    )

    VERTEX_AI_AVAILABLE = True
except ImportError:
    VERTEX_AI_AVAILABLE = False
    logging.warning("Vertex AI SDK not available. Advanced SQL generation disabled.")

from config.secure_config import load_database_config, get_connection_string

logger = logging.getLogger(__name__)


@dataclass
class QueryResult:
    """Structure for database query results"""

    success: bool
    data: List[Dict[str, Any]]
    query: str
    row_count: int
    error_message: Optional[str] = None
    tables_used: List[str] = None


@dataclass
class DatabaseSchema:
    """Structure for database schema information"""

    tables: Dict[str, Dict[str, str]]
    relationships: Dict[str, List[str]]
    table_descriptions: Dict[str, str]


class AdvancedDatabaseMCP:
    """
    Advanced Database Integration with Gemini-powered SQL generation
    Handles complex queries including JOINs and aggregations
    """

    def __init__(self):
        """Initialize the advanced database service"""
        self.db_config = None
        self.connection = None
        self.schema_info = self._get_database_schema()
        self.model = None
        self._initialize_connection()
        self._initialize_gemini()

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

    def _initialize_gemini(self):
        """Initialize Gemini model with function calling capabilities"""
        if not VERTEX_AI_AVAILABLE:
            logger.error("Vertex AI SDK not available")
            return

        try:
            # Initialize Vertex AI (you may need to set project and location)
            # vertexai.init(project="your-project-id", location="us-central1")

            # Define SQL generation function
            sql_generation_func = FunctionDeclaration(
                name="generate_sql_query",
                description="Generate complex SQL queries for hospital database operations including JOINs, aggregations, and filters",
                parameters={
                    "type": "object",
                    "properties": {
                        "query_type": {
                            "type": "string",
                            "description": "Type of SQL query needed",
                            "enum": ["SELECT", "JOIN", "AGGREGATE", "COMPLEX"],
                        },
                        "tables": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of tables to query from",
                        },
                        "columns": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Columns to select or include in query",
                        },
                        "joins": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "type": {
                                        "type": "string",
                                        "enum": ["INNER", "LEFT", "RIGHT", "FULL"],
                                    },
                                    "table": {"type": "string"},
                                    "condition": {"type": "string"},
                                },
                            },
                            "description": "JOIN operations to perform",
                        },
                        "filters": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "WHERE conditions to apply",
                        },
                        "aggregations": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Aggregation functions to apply (COUNT, SUM, AVG, etc.)",
                        },
                        "order_by": {
                            "type": "string",
                            "description": "ORDER BY clause",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "LIMIT for number of results",
                        },
                    },
                    "required": ["query_type", "tables"],
                },
            )

            # Define database analysis function
            analysis_func = FunctionDeclaration(
                name="analyze_user_query",
                description="Analyze user query to understand what information they need from the hospital database",
                parameters={
                    "type": "object",
                    "properties": {
                        "intent": {
                            "type": "string",
                            "description": "Primary intent of the user query",
                            "enum": [
                                "patient_information",
                                "room_status",
                                "equipment_inventory",
                                "staff_lookup",
                                "hospital_statistics",
                                "occupancy_report",
                                "patient_history",
                                "room_assignment",
                                "equipment_location",
                                "patient_room_join",
                                "patient_equipment_usage",
                                "comprehensive_report",
                            ],
                        },
                        "entities": {
                            "type": "object",
                            "properties": {
                                "patient_name": {"type": "string"},
                                "room_number": {"type": "string"},
                                "equipment_type": {"type": "string"},
                                "staff_name": {"type": "string"},
                                "date_range": {"type": "string"},
                                "department": {"type": "string"},
                            },
                            "description": "Extracted entities from user query",
                        },
                        "complexity": {
                            "type": "string",
                            "enum": ["simple", "moderate", "complex"],
                            "description": "Complexity level of the required query",
                        },
                        "requires_joins": {
                            "type": "boolean",
                            "description": "Whether the query requires JOIN operations",
                        },
                    },
                    "required": ["intent", "complexity", "requires_joins"],
                },
            )

            # Create tools
            sql_tool = Tool(function_declarations=[sql_generation_func, analysis_func])

            # Initialize model with tools
            self.model = GenerativeModel("gemini-1.5-pro", tools=[sql_tool])

            logger.info(
                "Gemini model initialized with SQL function calling capabilities"
            )

        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {e}")

    def _get_database_schema(self) -> DatabaseSchema:
        """Get database schema information for context"""
        tables = {
            "users": {
                "id": "INTEGER PRIMARY KEY",
                "full_name": "VARCHAR(255) NOT NULL",
                "email": "VARCHAR(255) UNIQUE NOT NULL",
                "phone_number": "JSONB",
                "emergency_contact": "JSONB",
                "password_hash": "VARCHAR(255) NOT NULL",
                "role": "VARCHAR(50) NOT NULL",
                "staff_type": "VARCHAR(100)",
            },
            "patient_records": {
                "id": "INTEGER PRIMARY KEY",
                "user_id": "INTEGER REFERENCES users(id)",
                "date_of_birth": "DATE",
                "gender": "CHAR(1)",
                "blood_group": "VARCHAR(10)",
                "allergies": "TEXT",
                "medical_history": "TEXT",
                "emergency_contact": "JSONB",
                "contact_phone": "JSONB",
            },
            "rooms": {
                "id": "INTEGER PRIMARY KEY",
                "room_number": "VARCHAR(50) NOT NULL",
                "room_type": "VARCHAR(100) NOT NULL",
                "bed_capacity": "INTEGER",
                "table_count": "INTEGER",
                "has_oxygen_outlet": "BOOLEAN",
                "floor_number": "INTEGER",
                "notes": "TEXT",
            },
            "occupancy": {
                "id": "INTEGER PRIMARY KEY",
                "room_id": "INTEGER REFERENCES rooms(id)",
                "bed_number": "INTEGER",
                "patient_id": "INTEGER REFERENCES patient_records(id)",
                "attendee": "JSONB",
                "assigned_at": "TIMESTAMP",
                "discharged_at": "TIMESTAMP",
                "tools": "JSONB",
                "hospital_inventory": "JSONB",
            },
            "tools": {
                "id": "INTEGER PRIMARY KEY",
                "tool_name": "VARCHAR(255) NOT NULL",
                "description": "TEXT",
                "category": "VARCHAR(100)",
                "quantity_total": "INTEGER",
                "quantity_available": "INTEGER",
                "location_storage_id": "INTEGER REFERENCES storage_rooms(id)",
                "location_description": "VARCHAR(255)",
                "purchase_date": "DATE",
                "last_maintenance_date": "DATE",
            },
            "storage_rooms": {
                "id": "INTEGER PRIMARY KEY",
                "storage_number": "VARCHAR(50) NOT NULL",
                "storage_type": "VARCHAR(100) NOT NULL",
                "floor_number": "INTEGER",
                "capacity": "INTEGER",
                "notes": "TEXT",
            },
            "hospital_inventory": {
                "id": "INTEGER PRIMARY KEY",
                "item_name": "VARCHAR(255) NOT NULL",
                "item_type": "VARCHAR(100)",
                "quantity_total": "INTEGER",
                "quantity_available": "INTEGER",
                "location_storage_id": "INTEGER REFERENCES storage_rooms(id)",
                "location_description": "VARCHAR(255)",
                "details": "TEXT",
                "expiry_date": "DATE",
            },
        }

        relationships = {
            "users_patient_records": ["users.id = patient_records.user_id"],
            "rooms_occupancy": ["rooms.id = occupancy.room_id"],
            "patient_records_occupancy": ["patient_records.id = occupancy.patient_id"],
            "storage_rooms_tools": ["storage_rooms.id = tools.location_storage_id"],
            "storage_rooms_hospital_inventory": [
                "storage_rooms.id = hospital_inventory.location_storage_id"
            ],
        }

        table_descriptions = {
            "users": "Contains user information including patients and staff",
            "patient_records": "Medical records and personal information for patients",
            "rooms": "Hospital room information including capacity and type",
            "occupancy": "Current and historical room assignments for patients",
            "tools": "Medical tools and equipment inventory",
            "storage_rooms": "Storage locations for equipment and inventory",
            "hospital_inventory": "General hospital inventory items",
        }

        return DatabaseSchema(
            tables=tables,
            relationships=relationships,
            table_descriptions=table_descriptions,
        )

    def _get_connection(self):
        """Get database connection with automatic retry"""
        if not DB_AVAILABLE or not self.db_config:
            raise RuntimeError("Database not available")

        try:
            if self.connection and not self.connection.closed:
                return self.connection

            db_config = self.db_config["database"]
            self.connection = psycopg2.connect(**db_config)
            return self.connection
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise

    def generate_advanced_sql(self, user_query: str) -> str:
        """
        Generate advanced SQL queries using Nebius model with function calling
        Similar to Google Cloud's approach but adapted for Nebius
        """
        try:
            # Import here to avoid circular imports
            try:
                from ..models.nebius_model import NebiusModel
            except ImportError:
                # Try direct import if relative import fails
                from models.nebius_model import NebiusModel

            nebius_model = NebiusModel()

            if not nebius_model.is_available():
                # Fallback to pattern matching if Nebius is unavailable
                return self._fallback_sql_generation(user_query)

            # Create a detailed prompt for SQL generation with function calling
            system_prompt = self._build_sql_generation_system_prompt()

            # Prepare the function declaration for SQL generation
            sql_function_declaration = {
                "name": "generate_sql_query",
                "description": "Generate SQL queries for hospital database operations including JOINs, aggregations, and filters",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query_type": {
                            "type": "string",
                            "description": "Type of SQL query needed",
                            "enum": ["SELECT", "JOIN", "AGGREGATE", "COMPLEX"],
                        },
                        "main_tables": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Primary tables to query from",
                        },
                        "join_operations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "type": {"type": "string"},
                                    "table": {"type": "string"},
                                    "condition": {"type": "string"},
                                },
                            },
                            "description": "JOIN operations to perform",
                        },
                        "columns": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Columns to select",
                        },
                        "where_conditions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "WHERE clause conditions",
                        },
                        "order_by": {
                            "type": "string",
                            "description": "ORDER BY clause",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "LIMIT for results",
                        },
                        "sql_query": {
                            "type": "string",
                            "description": "The complete SQL query",
                        },
                    },
                    "required": ["query_type", "sql_query"],
                },
            }

            # Build the user query with context
            user_prompt = f"""
            Based on the hospital database schema guide and user request, generate an appropriate SQL query.
            
            USER REQUEST: {user_query}
            
            Please analyze the request and generate the appropriate SQL query following the schema guide interpretation rules:
            1. For patient information with room details: JOIN users, patient_records, occupancy, and rooms tables
            2. For staff information: query users table with role filters and staff_type
            3. For equipment information: query tools and storage_rooms tables
            4. For equipment counts ("How many X do we have?"): use COUNT(*) and SUM(quantity_available) from tools table with tool_name ILIKE pattern
            5. For specific equipment types: tools.tool_name contains "Stethoscope", "Ventilator", "ECG Machine", "Defibrillator", etc.
            6. For blood group counts: use patient_records.blood_group
            7. For blood inventory: use hospital_inventory where item_type='blood_unit'
            8. For room availability: check occupancy.discharged_at IS NULL
            9. For statistics or counts: use appropriate aggregation functions
            10. Always use proper JOINs when data spans multiple tables
            11. Limit results appropriately (usually 30-50 for lists)
            12. Follow the query interpretation rules from the schema guide
            
            Use the generate_sql_query function to provide the SQL query.
            """

            # Use Nebius model to generate the SQL with hospital schema context
            response = nebius_model.generate_sql_query(
                user_request=user_query,
                # database_schema parameter is now optional and will use hospital schema by default
                max_tokens=1500,
                temperature=0.1,  # Low temperature for more deterministic SQL
            )

            # Extract SQL from the response
            sql_query = self._extract_sql_from_response(response, user_query)

            # Validate and fix common SQL issues
            sql_query = self._validate_and_fix_sql(sql_query, user_query)

            logger.info(f"Generated SQL using Nebius: {sql_query}")
            return sql_query

        except Exception as e:
            logger.error(f"Nebius SQL generation failed: {e}")
            # Fallback to pattern matching
            return self._fallback_sql_generation(user_query)

    def _load_hospital_schema_guide(self) -> str:
        """Load the hospital schema guide markdown file"""
        try:
            schema_guide_path = project_root / "data" / "hospital_schema_guide.md"
            with open(schema_guide_path, "r", encoding="utf-8") as f:
                content = f.read()
            logger.info("Hospital schema guide loaded successfully")
            return content
        except Exception as e:
            logger.error(f"Failed to load hospital schema guide: {e}")
            return self._get_fallback_schema_context()

    def _get_fallback_schema_context(self) -> str:
        """Get fallback schema context if the markdown file cannot be loaded"""
        return """
        # Hospital Database Schema (Fallback)
        
        ## Tables:
        - users: id, full_name, role (patient/staff/doctor/nurse), email, staff_type
        - patient_records: id, user_id, date_of_birth, gender, blood_group, medical_history, allergies
        - rooms: id, room_number, room_type, bed_capacity, floor_number
        - occupancy: id, patient_id, room_id, assigned_at, discharged_at
        - tools: id, tool_name, category, quantity_total, quantity_available, location_storage_id
        - storage_rooms: id, storage_number, storage_type, floor_number, capacity, notes
        - hospital_inventory: id, item_name, item_type, quantity_total, quantity_available, location_storage_id
        
        ## Key Relationships:
        - users.id = patient_records.user_id (patient details)
        - patient_records.id = occupancy.patient_id (room assignments)
        - occupancy.room_id = rooms.id (room details)
        - tools.location_storage_id = storage_rooms.id (equipment locations)
        - hospital_inventory.location_storage_id = storage_rooms.id
        
        ## Important Notes:
        - Blood group counts: use patient_records.blood_group
        - Blood inventory counts: use hospital_inventory where item_type='blood_unit'
        - Current room occupancy: occupancy table where discharged_at IS NULL
        """

    def _build_sql_generation_system_prompt(self) -> str:
        """Build system prompt for SQL generation with hospital schema context"""
        # Load the hospital schema guide markdown
        schema_guide_content = self._load_hospital_schema_guide()

        return f"""
        You are an expert SQL developer for a hospital management system. You generate precise SQL queries 
        based on user requests with full understanding of the hospital database structure.
        
        Use the following comprehensive hospital database schema guide:
        
        {schema_guide_content}
        
        ADDITIONAL SQL GENERATION GUIDELINES:
        1. Always use proper JOINs when data spans multiple tables
        2. Use LEFT JOINs for optional relationships (like room assignments)
        3. Use INNER JOINs for required relationships
        4. Include appropriate WHERE clauses for filtering
        5. Use meaningful aliases for tables (u for users, pr for patient_records, etc.)
        6. Limit results appropriately (usually 30-50 for lists)
        7. Order results logically
        8. Pay special attention to blood group vs blood inventory distinctions as outlined in the schema guide
        9. For current occupancy, filter by discharged_at IS NULL
        10. Use proper date formatting for timestamp comparisons
        
        Generate complete, syntactically correct PostgreSQL queries that follow the schema relationships and interpretation rules provided in the guide.
        """

    def _get_schema_description(self) -> str:
        """Get a detailed description of the database schema"""
        # Use the same schema guide content for consistency
        schema_guide_content = self._load_hospital_schema_guide()

        # Extract just the schema information for backward compatibility
        return f"""
        HOSPITAL DATABASE SCHEMA:
        
        Based on the comprehensive schema guide:
        
        {schema_guide_content}
        
        This provides complete table structures, relationships, and interpretation rules for all hospital database queries.
        """

    def _validate_and_fix_sql(self, sql_query: str, user_query: str) -> str:
        """Validate and fix common SQL issues generated by AI"""
        try:
            # Fix common column name issues in tools table
            if "tools" in sql_query.lower() or "equipment" in user_query.lower():
                # Fix incorrect column names for tools table
                sql_query = sql_query.replace("item_name", "tool_name")
                sql_query = sql_query.replace("t.item_name", "t.tool_name")

                # Check if the SQL looks problematic and use fallback instead
                if (
                    "item_name" in sql_query
                    or "stethoscope" in user_query.lower()
                    and "COUNT" not in sql_query.upper()
                ):
                    logger.warning(
                        "AI generated problematic SQL for equipment query, using fallback"
                    )
                    return self._fallback_sql_generation(user_query)

            return sql_query

        except Exception as e:
            logger.error(f"SQL validation failed: {e}")
            return sql_query

    def _extract_sql_from_response(self, response: str, user_query: str) -> str:
        """Extract SQL query from Nebius response"""
        try:
            # Look for SQL in the response (various possible formats)
            import re

            # Pattern 1: SQL wrapped in ```sql blocks
            sql_pattern = r"```sql\s*(.*?)\s*```"
            match = re.search(sql_pattern, response, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()

            # Pattern 2: SQL wrapped in ``` blocks
            sql_pattern = r"```\s*(SELECT.*?)\s*```"
            match = re.search(sql_pattern, response, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()

            # Pattern 3: Look for SELECT statements directly
            sql_pattern = r"(SELECT.*?(?:;|$))"
            match = re.search(sql_pattern, response, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()

            # Pattern 4: Extract anything that looks like SQL
            lines = response.split("\n")
            sql_lines = []
            in_sql = False

            for line in lines:
                line = line.strip()
                if line.upper().startswith("SELECT") or in_sql:
                    in_sql = True
                    sql_lines.append(line)
                    if line.endswith(";") or (line and not line.endswith(",")):
                        break

            if sql_lines:
                return " ".join(sql_lines).strip()

            # If no SQL found, fallback to pattern matching
            logger.warning(f"Could not extract SQL from response: {response[:200]}...")
            return self._fallback_sql_generation(user_query)

        except Exception as e:
            logger.error(f"Error extracting SQL from response: {e}")
            return self._fallback_sql_generation(user_query)

    def _fallback_sql_generation(self, user_query: str) -> str:
        """
        Fallback SQL generation using pattern matching
        (Original implementation as backup)
        """
        user_query_lower = user_query.lower()

        # Pattern: "list/top X patients with all relevant info"
        if (
            "top" in user_query_lower or "list" in user_query_lower
        ) and "patient" in user_query_lower:
            limit_match = re.search(r"(?:top|first)\s+(\d+)", user_query_lower)
            limit = int(limit_match.group(1)) if limit_match else 30

            return f"""
            SELECT 
                u.id,
                u.full_name as patient_name,
                pr.date_of_birth,
                pr.gender,
                pr.blood_group,
                pr.medical_history,
                pr.allergies,
                r.room_number,
                r.room_type,
                o.assigned_at as admission_date,
                CASE 
                    WHEN o.discharged_at IS NULL THEN 'Currently Admitted'
                    ELSE 'Discharged'
                END as status
            FROM users u
            INNER JOIN patient_records pr ON u.id = pr.user_id
            LEFT JOIN occupancy o ON pr.id = o.patient_id AND o.discharged_at IS NULL
            LEFT JOIN rooms r ON o.room_id = r.id
            WHERE u.role = 'patient'
            ORDER BY u.full_name
            LIMIT {limit}
            """

        # Pattern: "patients in room" or "room assignments"
        elif "patient" in user_query_lower and "room" in user_query_lower:
            return """
            SELECT 
                u.full_name as patient_name,
                pr.date_of_birth,
                pr.blood_group,
                r.room_number,
                r.room_type,
                r.bed_capacity,
                o.assigned_at,
                o.discharged_at,
                CASE 
                    WHEN o.discharged_at IS NULL THEN 'Currently Occupying'
                    ELSE 'Previously Occupied'
                END as occupancy_status
            FROM users u
            INNER JOIN patient_records pr ON u.id = pr.user_id
            INNER JOIN occupancy o ON pr.id = o.patient_id
            INNER JOIN rooms r ON o.room_id = r.id
            ORDER BY r.room_number, o.assigned_at DESC
            LIMIT 50
            """

        # Pattern: "room status" or "available rooms"
        elif "room" in user_query_lower and (
            "status" in user_query_lower or "available" in user_query_lower
        ):
            return """
            SELECT 
                r.room_number,
                r.room_type,
                r.bed_capacity,
                r.floor_number,
                CASE 
                    WHEN o.id IS NOT NULL AND o.discharged_at IS NULL THEN 'Occupied'
                    ELSE 'Available'
                END as status,
                u.full_name as current_patient,
                o.assigned_at
            FROM rooms r
            LEFT JOIN occupancy o ON r.id = o.room_id AND o.discharged_at IS NULL
            LEFT JOIN patient_records pr ON o.patient_id = pr.id
            LEFT JOIN users u ON pr.user_id = u.id
            ORDER BY r.room_number
            """

        # Pattern: "staff" or "doctors" or "nurses"
        elif any(
            word in user_query_lower
            for word in ["staff", "doctor", "nurse", "employee"]
        ):
            return """
            SELECT 
                u.full_name as staff_name,
                u.role,
                u.staff_type,
                u.email,
                COUNT(o.id) as patients_assigned
            FROM users u
            LEFT JOIN occupancy o ON u.full_name = o.attendee->>'name'
            WHERE u.role IN ('staff', 'admin', 'doctor', 'nurse')
            GROUP BY u.id, u.full_name, u.role, u.staff_type, u.email
            ORDER BY u.staff_type, u.full_name
            """

        # Pattern: "how many [equipment]" - specific count queries
        elif "how many" in user_query_lower and any(
            equipment in user_query_lower
            for equipment in [
                "stethoscope",
                "ventilator",
                "ecg",
                "defibrillator",
                "blood pressure monitor",
                "pulse oximeter",
                "infusion pump",
                "thermometer",
            ]
        ):
            # Extract equipment type from query
            equipment_type = None
            for equipment in [
                "stethoscope",
                "ventilator",
                "ecg",
                "defibrillator",
                "blood pressure monitor",
                "pulse oximeter",
                "infusion pump",
                "thermometer",
            ]:
                if equipment in user_query_lower:
                    equipment_type = equipment
                    break

            if equipment_type:
                # Handle special cases for equipment names
                if equipment_type == "ecg":
                    search_pattern = "ECG Machine"
                elif equipment_type == "blood pressure monitor":
                    search_pattern = "Blood Pressure Monitor"
                elif equipment_type == "pulse oximeter":
                    search_pattern = "Pulse Oximeter"
                elif equipment_type == "infusion pump":
                    search_pattern = "Infusion Pump"
                else:
                    search_pattern = equipment_type.title()

                return f"""
                SELECT 
                    '{search_pattern}' as equipment_type,
                    COUNT(*) as total_units,
                    SUM(t.quantity_available) as available_units,
                    SUM(t.quantity_total) as total_capacity,
                    ROUND(CAST(AVG(t.quantity_available::numeric / NULLIF(t.quantity_total::numeric, 0)) * 100 AS numeric), 2) as avg_availability_percentage
                FROM tools t
                WHERE t.tool_name ILIKE '%{search_pattern}%'
                GROUP BY '{search_pattern}'
                HAVING COUNT(*) > 0
                """

        # Pattern: "equipment" or "tools" - general listing
        elif any(
            word in user_query_lower
            for word in ["equipment", "tool", "medical", "device"]
        ):
            return """
            SELECT 
                t.tool_name,
                t.category,
                t.quantity_total,
                t.quantity_available,
                t.location_description,
                sr.storage_number,
                sr.storage_type,
                ROUND(CAST((t.quantity_available::numeric / NULLIF(t.quantity_total::numeric, 0)) * 100 AS numeric), 2) as availability_percentage
            FROM tools t
            LEFT JOIN storage_rooms sr ON t.location_storage_id = sr.id
            WHERE t.quantity_total > 0
            ORDER BY t.category, t.tool_name
            """

        # Pattern: "hospital statistics" or "overview"
        elif any(
            word in user_query_lower
            for word in ["statistic", "overview", "summary", "total", "count"]
        ):
            return """
            SELECT 
                'Total Patients' as metric,
                COUNT(*) as value,
                'people' as unit
            FROM users WHERE role = 'patient'
            UNION ALL
            SELECT 
                'Active Admissions' as metric,
                COUNT(*) as value,
                'patients' as unit
            FROM occupancy WHERE discharged_at IS NULL
            UNION ALL
            SELECT 
                'Total Rooms' as metric,
                COUNT(*) as value,
                'rooms' as unit
            FROM rooms
            UNION ALL
            SELECT 
                'Available Rooms' as metric,
                COUNT(*) as value,
                'rooms' as unit
            FROM rooms r
            LEFT JOIN occupancy o ON r.id = o.room_id AND o.discharged_at IS NULL
            WHERE o.id IS NULL
            UNION ALL
            SELECT 
                'Total Equipment Items' as metric,
                SUM(quantity_total) as value,
                'items' as unit
            FROM tools
            """

        # Default comprehensive query
        else:
            return """
            SELECT 
                'Use more specific queries' as suggestion,
                'Try: "top 30 patients", "room status", "hospital statistics", "staff list"' as examples
            """

    def execute_query(self, sql_query: str) -> QueryResult:
        """Execute SQL query and return structured results"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # Clean and validate query
            sql_query = sql_query.strip()
            if not sql_query.upper().startswith("SELECT"):
                raise ValueError("Only SELECT queries are allowed")

            # Extract table names
            tables_used = self._extract_table_names(sql_query)

            cursor.execute(sql_query)
            results = cursor.fetchall()

            # Convert to list of dictionaries
            data = [dict(row) for row in results]

            cursor.close()

            return QueryResult(
                success=True,
                data=data,
                query=sql_query,
                row_count=len(data),
                tables_used=tables_used,
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

    def _extract_table_names(self, sql_query: str) -> List[str]:
        """Extract table names from SQL query"""
        patterns = [
            r"FROM\s+(\w+)",
            r"JOIN\s+(\w+)",
        ]

        tables = set()
        for pattern in patterns:
            matches = re.findall(pattern, sql_query, re.IGNORECASE)
            tables.update(matches)

        return list(tables)

    def format_advanced_response(
        self, query_result: QueryResult, user_query: str
    ) -> str:
        """Format database results with enhanced presentation"""
        if not query_result.success:
            return f"❌ **Database Error**: {query_result.error_message}"

        if query_result.row_count == 0:
            return "📊 No matching records found in the hospital database."

        # Header with context
        response = (
            f"📊 **Hospital Database Results** ({query_result.row_count} records)\n"
        )
        if query_result.tables_used and len(query_result.tables_used) > 1:
            response += f"*Query used {len(query_result.tables_used)} tables: {', '.join(query_result.tables_used)}*\n\n"

        data = query_result.data

        # Smart formatting based on content
        if self._is_patient_data(data):
            response += self._format_patient_data(data)
        elif self._is_room_data(data):
            response += self._format_room_data(data)
        elif self._is_staff_data(data):
            response += self._format_staff_data(data)
        elif self._is_equipment_data(data):
            response += self._format_equipment_data(data)
        elif self._is_statistics_data(data):
            response += self._format_statistics_data(data)
        else:
            response += self._format_generic_data(data)

        return response

    def _is_patient_data(self, data: List[Dict]) -> bool:
        """Check if data contains patient information"""
        if not data:
            return False
        patient_fields = [
            "patient_name",
            "full_name",
            "date_of_birth",
            "blood_group",
            "medical_history",
        ]
        return any(field in data[0] for field in patient_fields)

    def _is_room_data(self, data: List[Dict]) -> bool:
        """Check if data contains room information"""
        if not data:
            return False
        room_fields = ["room_number", "room_type", "bed_capacity"]
        return any(field in data[0] for field in room_fields)

    def _is_staff_data(self, data: List[Dict]) -> bool:
        """Check if data contains staff information"""
        if not data:
            return False
        staff_fields = ["staff_name", "staff_type", "patients_assigned"]
        return any(field in data[0] for field in staff_fields)

    def _is_equipment_data(self, data: List[Dict]) -> bool:
        """Check if data contains equipment information"""
        if not data:
            return False
        equipment_fields = ["tool_name", "category", "quantity_available"]
        return any(field in data[0] for field in equipment_fields)

    def _is_statistics_data(self, data: List[Dict]) -> bool:
        """Check if data contains statistics"""
        if not data:
            return False
        return "metric" in data[0] and "value" in data[0]

    def _format_patient_data(self, data: List[Dict]) -> str:
        """Format patient information"""
        response = "👥 **Patient Information:**\n\n"

        for i, patient in enumerate(data[:25], 1):  # Limit display
            # Try different name fields
            name = (
                patient.get("patient_name")
                or patient.get("full_name")
                or patient.get("name")
                or "Unknown Patient"
            )
            response += f"**{i}. {name}**\n"

            # Key information
            if patient.get("date_of_birth"):
                response += f"   📅 DOB: {patient['date_of_birth']}\n"
            if patient.get("gender"):
                response += f"   👤 Gender: {patient['gender']}\n"
            if patient.get("blood_group"):
                response += f"   🩸 Blood Group: {patient['blood_group']}\n"
            if patient.get("email"):
                response += f"   📧 Email: {patient['email']}\n"
            if patient.get("room_number"):
                response += f"   🏥 Room: {patient['room_number']} ({patient.get('room_type', 'N/A')})\n"
            if (
                patient.get("medical_history")
                and patient["medical_history"] != "Standard medical history"
            ):
                response += f"   📋 Medical History: {patient['medical_history']}\n"
            if patient.get("allergies"):
                response += f"   ⚠️ Allergies: {patient['allergies']}\n"
            if patient.get("status"):
                response += f"   📊 Status: {patient['status']}\n"
            if patient.get("assigned_at"):
                response += f"   📝 Admitted: {patient['assigned_at']}\n"
            if patient.get("discharged_at"):
                response += f"   📤 Discharged: {patient['discharged_at']}\n"

            response += "\n"

        if len(data) > 25:
            response += f"... and {len(data) - 25} more patients\n"

        return response

    def _format_room_data(self, data: List[Dict]) -> str:
        """Format room information"""
        response = "🏥 **Room Information:**\n\n"

        for room in data[:30]:
            room_num = room.get("room_number", "Unknown")
            status = room.get("status", "Unknown")

            response += f"**Room {room_num}** - {status}\n"
            response += f"   🏠 Type: {room.get('room_type', 'N/A')}\n"
            response += f"   🛏️ Capacity: {room.get('bed_capacity', 'N/A')} beds\n"

            if room.get("current_patient"):
                response += f"   👤 Patient: {room['current_patient']}\n"
                if room.get("assigned_at"):
                    response += f"   📅 Since: {room['assigned_at']}\n"

            response += "\n"

        return response

    def _format_staff_data(self, data: List[Dict]) -> str:
        """Format staff information"""
        response = "👨‍⚕️ **Staff Information:**\n\n"

        for staff in data:
            name = staff.get("staff_name", "Unknown")
            role = staff.get("staff_type", staff.get("role", "N/A"))

            response += f"**{name}** - {role}\n"
            if staff.get("email"):
                response += f"   📧 {staff['email']}\n"
            if staff.get("patients_assigned"):
                response += f"   👥 Patients Assigned: {staff['patients_assigned']}\n"
            response += "\n"

        return response

    def _format_equipment_data(self, data: List[Dict]) -> str:
        """Format equipment information"""
        response = "🔧 **Equipment Inventory:**\n\n"

        current_category = None
        for equipment in data:
            category = equipment.get("category", "Other")
            if category != current_category:
                response += f"**{category}:**\n"
                current_category = category

            name = equipment.get("tool_name", "Unknown")
            available = equipment.get("quantity_available", 0)
            total = equipment.get("quantity_total", 0)

            response += f"   • {name}: {available}/{total} available"

            if equipment.get("availability_percentage"):
                response += f" ({equipment['availability_percentage']}%)"

            if equipment.get("location_description"):
                response += f" - {equipment['location_description']}"

            response += "\n"

        return response

    def _format_statistics_data(self, data: List[Dict]) -> str:
        """Format statistics information"""
        response = "📊 **Hospital Statistics:**\n\n"

        for stat in data:
            metric = stat.get("metric", "Unknown Metric")
            value = stat.get("value", "N/A")
            unit = stat.get("unit", "")

            response += f"• **{metric}:** {value} {unit}\n"

        return response

    def _format_generic_data(self, data: List[Dict]) -> str:
        """Format generic data"""
        response = "📋 **Query Results:**\n\n"

        for i, record in enumerate(data[:10], 1):
            # Try to get a name for the record
            name = (
                record.get("full_name")
                or record.get("patient_name")
                or record.get("staff_name")
                or record.get("name")
                or f"Record {i}"
            )

            response += f"**{name}:**\n"
            for key, value in record.items():
                if value is not None and key not in [
                    "full_name",
                    "patient_name",
                    "staff_name",
                    "name",
                ]:
                    formatted_key = key.replace("_", " ").title()
                    response += f"   • {formatted_key}: {value}\n"
            response += "\n"

        if len(data) > 10:
            response += f"... and {len(data) - 10} more records\n"

        return response

    def _analyze_query_intent(self, user_query: str) -> Dict[str, Any]:
        """
        Analyze user query to understand its intent and content
        Returns a summary with intent classification
        """
        try:
            # Import here to avoid circular imports
            try:
                from ..models.nebius_model import NebiusModel
            except ImportError:
                # Try direct import if relative import fails
                from models.nebius_model import NebiusModel

            nebius_model = NebiusModel()

            if not nebius_model.is_available():
                # Fallback to simple heuristic analysis
                return self._fallback_query_analysis(user_query)

            analysis_prompt = f"""
            Analyze the following user query and determine if it requires hospital database access.
            
            USER QUERY: "{user_query}"
            
            CRITERIA FOR DATABASE QUERIES:
            - Requests for specific patient information, lists, or records
            - Queries about room status, availability, or assignments
            - Staff information requests (lists, schedules, assignments)
            - Equipment/tools inventory, availability, or location queries
            - Medical equipment by category (Surgical, Diagnostic, Life Support, Monitoring)
            - Equipment maintenance schedules or status
            - Hospital statistics or operational data
            - Storage room contents or equipment locations
            - Any request that needs to retrieve stored hospital data
            
            SPECIFIC EQUIPMENT/TOOLS QUERIES INCLUDE:
            - Availability of medical equipment (ventilators, ECG machines, defibrillators, etc.)
            - Location of equipment in storage rooms
            - Equipment by category or type
            - Maintenance schedules or equipment status
            - Inventory counts of medical tools
            - Equipment in specific storage locations
            
            CRITERIA FOR NON-DATABASE QUERIES:
            - General medical knowledge questions (symptoms, treatments, definitions)
            - Casual conversations (greetings, thanks, weather)
            - Educational questions about medical concepts
            - Personal conversations or social interactions
            - Requests for explanations of medical terms or conditions
            - How to use medical equipment (procedural questions)
            
            Classify this query as either:
            A) DATABASE QUERY - requires accessing hospital database
            B) NON-DATABASE QUERY - general conversation/medical knowledge
            
            Provide your classification and brief reasoning.
            """

            # Use a low temperature for consistent analysis
            response = nebius_model.generate_response(
                prompt=analysis_prompt, max_tokens=300, temperature=0.1
            )

            # Parse the response to determine database relevance
            is_db_related = self._parse_intent_analysis(response, user_query)

            return {
                "is_database_related": is_db_related,
                "analysis": response,
                "method": "ai_analysis",
            }

        except Exception as e:
            logger.warning(
                f"AI query analysis failed: {e}, falling back to heuristic analysis"
            )
            return self._fallback_query_analysis(user_query)

    def _parse_intent_analysis(
        self, analysis_response: str, original_query: str
    ) -> bool:
        """
        Parse the AI analysis response to determine if the query is database-related
        """
        analysis_lower = analysis_response.lower()
        query_lower = original_query.lower()

        # Strong indicators that it's database-related
        positive_indicators = [
            "database query",
            "a) database query",
            "database access",
            "requires database",
            "hospital database",
            "data retrieval",
            "hospital data",
            "requires querying",
            "medical records",
            "patient information",
            "staff details",
            "room information",
            "equipment data",
            "equipment inventory",
            "tools data",
            "medical equipment",
            "equipment availability",
            "equipment location",
            "storage information",
            "maintenance data",
            "hospital operations",
            "statistics",
            "reports",
            "inventory",
            "occupancy",
            "stored hospital data",
            "accessing hospital database",
            "equipment by category",
            "surgical equipment",
            "diagnostic equipment",
            "monitoring equipment",
            "life support equipment",
        ]

        # Strong indicators that it's NOT database-related
        negative_indicators = [
            "non-database query",
            "b) non-database query",
            "general conversation",
            "medical knowledge",
            "not database",
            "no database",
            "not hospital data",
            "not data retrieval",
            "general question",
            "conversation",
            "greeting",
            "explanation",
            "how to",
            "what is",
            "definition",
            "concept",
            "general medical",
            "not related to hospital database",
            "does not require database",
            "educational",
            "informational",
            "conversational",
            "casual",
            "social interaction",
            "weather",
            "personal question",
            "general inquiry",
        ]

        # Count positive vs negative indicators
        positive_score = sum(
            1 for indicator in positive_indicators if indicator in analysis_lower
        )
        negative_score = sum(
            1 for indicator in negative_indicators if indicator in analysis_lower
        )

        # Also check the original query for obvious database terms
        hospital_terms = [
            "patient",
            "room",
            "staff",
            "doctor",
            "nurse",
            "equipment",
            "medical",
            "hospital",
            "bed",
            "admission",
            "discharge",
        ]

        query_score = sum(1 for term in hospital_terms if term in query_lower)

        # Decision logic
        if negative_score > positive_score:
            return False
        elif positive_score > 0 or query_score >= 2:
            return True
        elif query_score >= 1 and len(query_lower.split()) <= 5:
            return True  # Short queries with hospital terms are likely database queries
        else:
            return False

    def _fallback_query_analysis(self, user_query: str) -> Dict[str, Any]:
        """
        Fallback heuristic analysis when AI is not available
        """
        query_lower = user_query.lower()

        # Hospital domain terms
        hospital_entities = [
            "patient",
            "patients",
            "doctor",
            "doctors",
            "nurse",
            "nurses",
            "staff",
            "room",
            "rooms",
            "bed",
            "beds",
            "equipment",
            "tools",
            "medical",
            "hospital",
            "ward",
            "icu",
            "emergency",
            "pharmacy",
            "lab",
            "storage",
            "inventory",
        ]

        # Specific medical equipment terms
        medical_equipment = [
            "ventilator",
            "ventilators",
            "ecg machine",
            "ecg",
            "defibrillator",
            "defibrillators",
            "stethoscope",
            "stethoscopes",
            "blood pressure monitor",
            "pulse oximeter",
            "infusion pump",
            "thermometer",
            "thermometers",
            "surgical equipment",
            "diagnostic equipment",
            "life support",
            "monitoring equipment",
        ]

        # Equipment categories from the tools table
        equipment_categories = [
            "surgical",
            "diagnostic",
            "life support",
            "monitoring",
        ]

        # Storage locations
        storage_locations = [
            "medical equipment storage",
            "laboratory storage",
            "emergency equipment storage",
            "surgical supplies storage",
            "pharmaceutical storage",
            "storage room",
            "storage rooms",
        ]

        # Data request terms
        data_request_terms = [
            "list",
            "show",
            "display",
            "get",
            "find",
            "search",
            "count",
            "how many",
            "total",
            "statistics",
            "report",
            "information",
            "details",
            "records",
            "data",
            "lookup",
            "retrieve",
        ]

        # Information seeking patterns
        info_patterns = [
            "who are",
            "what is",
            "where are",
            "which",
            "tell me about",
            "give me",
            "i need",
            "show me",
            "find me",
        ]

        # Score the query
        hospital_score = sum(1 for term in hospital_entities if term in query_lower)
        equipment_score = sum(1 for term in medical_equipment if term in query_lower)
        category_score = sum(1 for term in equipment_categories if term in query_lower)
        storage_score = sum(1 for term in storage_locations if term in query_lower)
        data_score = sum(1 for term in data_request_terms if term in query_lower)
        pattern_score = sum(1 for pattern in info_patterns if pattern in query_lower)

        # Decision logic for fallback - be more conservative
        total_score = (
            hospital_score
            + equipment_score
            + category_score
            + storage_score
            + data_score
            + pattern_score
        )

        # Strong non-database indicators
        non_db_patterns = [
            "hello",
            "hi",
            "good morning",
            "good afternoon",
            "good evening",
            "thank you",
            "thanks",
            "weather",
            "joke",
            "how are you",
            "what is",
            "how to",
            "explain",
            "definition",
            "symptoms of",
            "how does",
            "what are the symptoms",
            "treat",
            "treatment",
            "how to use",
            "procedure",
            "steps to",
        ]

        non_db_score = sum(1 for pattern in non_db_patterns if pattern in query_lower)

        # If it has strong non-database indicators, it's likely not a database query
        if non_db_score >= 1:
            is_db_related = False
        # Strong equipment/tools queries - high priority for database access
        elif equipment_score >= 1 or storage_score >= 1:
            is_db_related = True
        # Equipment category queries
        elif category_score >= 1 and (data_score >= 1 or pattern_score >= 1):
            is_db_related = True
        # If query has hospital terms AND data request terms, likely database query
        elif hospital_score >= 1 and data_score >= 1:
            is_db_related = True
        # If it has a high total score but no clear non-db indicators
        elif total_score >= 3 and non_db_score == 0:
            is_db_related = True
        # Conservative default
        else:
            is_db_related = False

        return {
            "is_database_related": is_db_related,
            "analysis": f"Heuristic analysis: hospital_score={hospital_score}, equipment_score={equipment_score}, category_score={category_score}, storage_score={storage_score}, data_score={data_score}, pattern_score={pattern_score}, non_db_score={non_db_score}, total={total_score}",
            "method": "heuristic_analysis",
        }

    def is_database_query(self, user_query: str) -> bool:
        """
        Check if the user query is a database-related query using intelligent analysis
        """
        try:
            # Generate query summary and intent analysis
            analysis_result = self._analyze_query_intent(user_query)

            logger.debug(f"Query analysis for '{user_query}': {analysis_result}")

            return analysis_result["is_database_related"]

        except Exception as e:
            logger.error(f"Error in database query detection: {e}")
            # Fallback to simple keyword matching in case of error
            return self._simple_keyword_fallback(user_query)

    def _simple_keyword_fallback(self, user_query: str) -> bool:
        """Simple keyword fallback for emergency cases"""
        essential_keywords = [
            "patient",
            "room",
            "staff",
            "doctor",
            "nurse",
            "equipment",
            "medical",
            "hospital",
            "list",
            "show",
            "how many",
            "count",
        ]

        user_query_lower = user_query.lower()
        return any(keyword in user_query_lower for keyword in essential_keywords)

    def process_advanced_query(self, user_query: str) -> str:
        """Process complex queries with advanced SQL generation"""
        try:
            logger.info(f"Processing advanced query: {user_query}")

            # Generate advanced SQL
            sql_query = self.generate_advanced_sql(user_query)
            logger.debug(f"Generated SQL: {sql_query}")

            # Execute query
            result = self.execute_query(sql_query)

            # Format response
            formatted_response = self.format_advanced_response(result, user_query)

            return formatted_response

        except Exception as e:
            logger.error(f"Advanced query processing failed: {e}")
            return f"❌ Error processing advanced query: {str(e)}"


# Global instance
advanced_database_mcp = AdvancedDatabaseMCP()
