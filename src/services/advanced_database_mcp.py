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
        Part
    )
    VERTEX_AI_AVAILABLE = True
except ImportError:
    VERTEX_AI_AVAILABLE = False
    logging.warning("Vertex AI SDK not available. Advanced SQL generation disabled.")

from secure_config import load_database_config, get_connection_string

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
                            "enum": ["SELECT", "JOIN", "AGGREGATE", "COMPLEX"]
                        },
                        "tables": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of tables to query from"
                        },
                        "columns": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Columns to select or include in query"
                        },
                        "joins": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "type": {"type": "string", "enum": ["INNER", "LEFT", "RIGHT", "FULL"]},
                                    "table": {"type": "string"},
                                    "condition": {"type": "string"}
                                }
                            },
                            "description": "JOIN operations to perform"
                        },
                        "filters": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "WHERE conditions to apply"
                        },
                        "aggregations": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Aggregation functions to apply (COUNT, SUM, AVG, etc.)"
                        },
                        "order_by": {
                            "type": "string",
                            "description": "ORDER BY clause"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "LIMIT for number of results"
                        }
                    },
                    "required": ["query_type", "tables"]
                }
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
                                "patient_information", "room_status", "equipment_inventory", 
                                "staff_lookup", "hospital_statistics", "occupancy_report",
                                "patient_history", "room_assignment", "equipment_location",
                                "patient_room_join", "patient_equipment_usage", "comprehensive_report"
                            ]
                        },
                        "entities": {
                            "type": "object",
                            "properties": {
                                "patient_name": {"type": "string"},
                                "room_number": {"type": "string"},
                                "equipment_type": {"type": "string"},
                                "staff_name": {"type": "string"},
                                "date_range": {"type": "string"},
                                "department": {"type": "string"}
                            },
                            "description": "Extracted entities from user query"
                        },
                        "complexity": {
                            "type": "string",
                            "enum": ["simple", "moderate", "complex"],
                            "description": "Complexity level of the required query"
                        },
                        "requires_joins": {
                            "type": "boolean",
                            "description": "Whether the query requires JOIN operations"
                        }
                    },
                    "required": ["intent", "complexity", "requires_joins"]
                }
            )
            
            # Create tools
            sql_tool = Tool(function_declarations=[sql_generation_func, analysis_func])
            
            # Initialize model with tools
            self.model = GenerativeModel(
                "gemini-1.5-pro",
                tools=[sql_tool]
            )
            
            logger.info("Gemini model initialized with SQL function calling capabilities")
            
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
                "staff_type": "VARCHAR(100)"
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
                "contact_phone": "JSONB"
            },
            "rooms": {
                "id": "INTEGER PRIMARY KEY",
                "room_number": "VARCHAR(50) NOT NULL",
                "room_type": "VARCHAR(100) NOT NULL",
                "bed_capacity": "INTEGER",
                "table_count": "INTEGER",
                "has_oxygen_outlet": "BOOLEAN",
                "floor_number": "INTEGER",
                "notes": "TEXT"
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
                "hospital_inventory": "JSONB"
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
                "last_maintenance_date": "DATE"
            },
            "storage_rooms": {
                "id": "INTEGER PRIMARY KEY",
                "storage_number": "VARCHAR(50) NOT NULL",
                "storage_type": "VARCHAR(100) NOT NULL",
                "floor_number": "INTEGER",
                "capacity": "INTEGER",
                "notes": "TEXT"
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
                "expiry_date": "DATE"
            }
        }
        
        relationships = {
            "users_patient_records": ["users.id = patient_records.user_id"],
            "rooms_occupancy": ["rooms.id = occupancy.room_id"],
            "patient_records_occupancy": ["patient_records.id = occupancy.patient_id"],
            "storage_rooms_tools": ["storage_rooms.id = tools.location_storage_id"],
            "storage_rooms_hospital_inventory": ["storage_rooms.id = hospital_inventory.location_storage_id"]
        }
        
        table_descriptions = {
            "users": "Contains user information including patients and staff",
            "patient_records": "Medical records and personal information for patients",
            "rooms": "Hospital room information including capacity and type",
            "occupancy": "Current and historical room assignments for patients",
            "tools": "Medical tools and equipment inventory",
            "storage_rooms": "Storage locations for equipment and inventory",
            "hospital_inventory": "General hospital inventory items"
        }
        
        return DatabaseSchema(
            tables=tables,
            relationships=relationships,
            table_descriptions=table_descriptions
        )
    
    def _get_connection(self):
        """Get database connection with automatic retry"""
        if not DB_AVAILABLE or not self.db_config:
            raise RuntimeError("Database not available")
            
        try:
            if self.connection and not self.connection.closed:
                return self.connection
                
            db_config = self.db_config['database']
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
            from ..models.nebius_model import NebiusModel
            
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
                            "enum": ["SELECT", "JOIN", "AGGREGATE", "COMPLEX"]
                        },
                        "main_tables": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Primary tables to query from"
                        },
                        "join_operations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "type": {"type": "string"},
                                    "table": {"type": "string"},
                                    "condition": {"type": "string"}
                                }
                            },
                            "description": "JOIN operations to perform"
                        },
                        "columns": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Columns to select"
                        },
                        "where_conditions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "WHERE clause conditions"
                        },
                        "order_by": {
                            "type": "string",
                            "description": "ORDER BY clause"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "LIMIT for results"
                        },
                        "sql_query": {
                            "type": "string",
                            "description": "The complete SQL query"
                        }
                    },
                    "required": ["query_type", "sql_query"]
                }
            }
            
            # Build the user query with context
            user_prompt = f"""
            Based on the following database schema and user request, generate an appropriate SQL query.
            
            DATABASE SCHEMA:
            {self._get_schema_description()}
            
            USER REQUEST: {user_query}
            
            Please analyze the request and generate the appropriate SQL query. Consider:
            1. If it needs patient information with room details, use JOINs between users, patient_records, occupancy, and rooms tables
            2. If it needs staff information, query from users table with appropriate role filters
            3. If it needs equipment information, query from tools and storage_rooms tables
            4. If it needs statistics or counts, use appropriate aggregation functions
            5. Always use proper JOINs when data spans multiple tables
            6. Limit results appropriately (usually 30-50 for lists)
            
            Use the generate_sql_query function to provide the SQL query.
            """
            
            # Use Nebius model to generate the SQL
            response = nebius_model.generate_sql_query(
                user_request=user_query,
                database_schema=self._get_schema_description(),
                max_tokens=1500,
                temperature=0.1  # Low temperature for more deterministic SQL
            )
            
            # Extract SQL from the response
            sql_query = self._extract_sql_from_response(response, user_query)
            
            logger.info(f"Generated SQL using Nebius: {sql_query}")
            return sql_query
            
        except Exception as e:
            logger.error(f"Nebius SQL generation failed: {e}")
            # Fallback to pattern matching
            return self._fallback_sql_generation(user_query)
    
    def _build_sql_generation_system_prompt(self) -> str:
        """Build system prompt for SQL generation"""
        return """
        You are an expert SQL developer for a hospital management system. You generate precise SQL queries 
        based on user requests. You have access to the following database schema:
        
        TABLES:
        - users: id, full_name, role (patient/staff/doctor/nurse), email, staff_type
        - patient_records: id, user_id, date_of_birth, gender, blood_group, medical_history, allergies
        - rooms: id, room_number, room_type, bed_capacity, floor_number
        - occupancy: id, patient_id, room_id, assigned_at, discharged_at
        - tools: id, tool_name, category, quantity_total, quantity_available, location_storage_id
        - storage_rooms: id, storage_number, storage_type, location_description
        
        KEY RELATIONSHIPS:
        - users.id = patient_records.user_id (patient details)
        - patient_records.id = occupancy.patient_id (room assignments)
        - occupancy.room_id = rooms.id (room details)
        - tools.location_storage_id = storage_rooms.id (equipment locations)
        
        GUIDELINES:
        1. Always use proper JOINs when data spans multiple tables
        2. Use LEFT JOINs for optional relationships (like room assignments)
        3. Use INNER JOINs for required relationships
        4. Include appropriate WHERE clauses for filtering
        5. Use meaningful aliases for tables
        6. Limit results appropriately
        7. Order results logically
        
        Generate complete, syntactically correct PostgreSQL queries.
        """
    
    def _get_schema_description(self) -> str:
        """Get a detailed description of the database schema"""
        return """
        HOSPITAL DATABASE SCHEMA:
        
        1. users table:
           - id (PRIMARY KEY)
           - full_name (patient/staff name)
           - role (patient, staff, doctor, nurse, admin)
           - email
           - staff_type (for staff roles)
        
        2. patient_records table:
           - id (PRIMARY KEY)
           - user_id (FOREIGN KEY to users.id)
           - date_of_birth
           - gender
           - blood_group
           - medical_history
           - allergies
        
        3. rooms table:
           - id (PRIMARY KEY)
           - room_number
           - room_type
           - bed_capacity
           - floor_number
        
        4. occupancy table:
           - id (PRIMARY KEY)
           - patient_id (FOREIGN KEY to patient_records.id)
           - room_id (FOREIGN KEY to rooms.id)
           - assigned_at (admission date)
           - discharged_at (discharge date, NULL if still admitted)
        
        5. tools table:
           - id (PRIMARY KEY)
           - tool_name
           - category
           - quantity_total
           - quantity_available
           - location_storage_id (FOREIGN KEY to storage_rooms.id)
        
        6. storage_rooms table:
           - id (PRIMARY KEY)
           - storage_number
           - storage_type
           - location_description
        """
    
    def _extract_sql_from_response(self, response: str, user_query: str) -> str:
        """Extract SQL query from Nebius response"""
        try:
            # Look for SQL in the response (various possible formats)
            import re
            
            # Pattern 1: SQL wrapped in ```sql blocks
            sql_pattern = r'```sql\s*(.*?)\s*```'
            match = re.search(sql_pattern, response, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
            
            # Pattern 2: SQL wrapped in ``` blocks
            sql_pattern = r'```\s*(SELECT.*?)\s*```'
            match = re.search(sql_pattern, response, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
            
            # Pattern 3: Look for SELECT statements directly
            sql_pattern = r'(SELECT.*?(?:;|$))'
            match = re.search(sql_pattern, response, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
            
            # Pattern 4: Extract anything that looks like SQL
            lines = response.split('\n')
            sql_lines = []
            in_sql = False
            
            for line in lines:
                line = line.strip()
                if line.upper().startswith('SELECT') or in_sql:
                    in_sql = True
                    sql_lines.append(line)
                    if line.endswith(';') or (line and not line.endswith(',')):
                        break
            
            if sql_lines:
                return ' '.join(sql_lines).strip()
            
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
        if ('top' in user_query_lower or 'list' in user_query_lower) and 'patient' in user_query_lower:
            limit_match = re.search(r'(?:top|first)\s+(\d+)', user_query_lower)
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
        elif 'patient' in user_query_lower and 'room' in user_query_lower:
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
        elif 'room' in user_query_lower and ('status' in user_query_lower or 'available' in user_query_lower):
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
        elif any(word in user_query_lower for word in ['staff', 'doctor', 'nurse', 'employee']):
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
        
        # Pattern: "equipment" or "tools"
        elif any(word in user_query_lower for word in ['equipment', 'tool', 'medical', 'device']):
            return """
            SELECT 
                t.tool_name,
                t.category,
                t.quantity_total,
                t.quantity_available,
                t.location_description,
                sr.storage_number,
                sr.storage_type,
                ROUND((t.quantity_available::float / t.quantity_total::float) * 100, 2) as availability_percentage
            FROM tools t
            LEFT JOIN storage_rooms sr ON t.location_storage_id = sr.id
            WHERE t.quantity_total > 0
            ORDER BY t.category, t.tool_name
            """
        
        # Pattern: "hospital statistics" or "overview"
        elif any(word in user_query_lower for word in ['statistic', 'overview', 'summary', 'total', 'count']):
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
            if not sql_query.upper().startswith('SELECT'):
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
                tables_used=tables_used
            )
            
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return QueryResult(
                success=False,
                data=[],
                query=sql_query,
                row_count=0,
                error_message=str(e)
            )
    
    def _extract_table_names(self, sql_query: str) -> List[str]:
        """Extract table names from SQL query"""
        patterns = [
            r'FROM\s+(\w+)',
            r'JOIN\s+(\w+)',
        ]
        
        tables = set()
        for pattern in patterns:
            matches = re.findall(pattern, sql_query, re.IGNORECASE)
            tables.update(matches)
        
        return list(tables)
    
    def format_advanced_response(self, query_result: QueryResult, user_query: str) -> str:
        """Format database results with enhanced presentation"""
        if not query_result.success:
            return f"❌ **Database Error**: {query_result.error_message}"
        
        if query_result.row_count == 0:
            return "📊 No matching records found in the hospital database."
        
        # Header with context
        response = f"📊 **Hospital Database Results** ({query_result.row_count} records)\n"
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
        patient_fields = ['patient_name', 'full_name', 'date_of_birth', 'blood_group', 'medical_history']
        return any(field in data[0] for field in patient_fields)
    
    def _is_room_data(self, data: List[Dict]) -> bool:
        """Check if data contains room information"""
        if not data:
            return False
        room_fields = ['room_number', 'room_type', 'bed_capacity']
        return any(field in data[0] for field in room_fields)
    
    def _is_staff_data(self, data: List[Dict]) -> bool:
        """Check if data contains staff information"""
        if not data:
            return False
        staff_fields = ['staff_name', 'staff_type', 'patients_assigned']
        return any(field in data[0] for field in staff_fields)
    
    def _is_equipment_data(self, data: List[Dict]) -> bool:
        """Check if data contains equipment information"""
        if not data:
            return False
        equipment_fields = ['tool_name', 'category', 'quantity_available']
        return any(field in data[0] for field in equipment_fields)
    
    def _is_statistics_data(self, data: List[Dict]) -> bool:
        """Check if data contains statistics"""
        if not data:
            return False
        return 'metric' in data[0] and 'value' in data[0]
    
    def _format_patient_data(self, data: List[Dict]) -> str:
        """Format patient information"""
        response = "👥 **Patient Information:**\n\n"
        
        for i, patient in enumerate(data[:25], 1):  # Limit display
            # Try different name fields
            name = (patient.get('patient_name') or 
                   patient.get('full_name') or 
                   patient.get('name') or 
                   'Unknown Patient')
            response += f"**{i}. {name}**\n"
            
            # Key information
            if patient.get('date_of_birth'):
                response += f"   📅 DOB: {patient['date_of_birth']}\n"
            if patient.get('gender'):
                response += f"   👤 Gender: {patient['gender']}\n"
            if patient.get('blood_group'):
                response += f"   🩸 Blood Group: {patient['blood_group']}\n"
            if patient.get('email'):
                response += f"   📧 Email: {patient['email']}\n"
            if patient.get('room_number'):
                response += f"   🏥 Room: {patient['room_number']} ({patient.get('room_type', 'N/A')})\n"
            if patient.get('medical_history') and patient['medical_history'] != 'Standard medical history':
                response += f"   📋 Medical History: {patient['medical_history']}\n"
            if patient.get('allergies'):
                response += f"   ⚠️ Allergies: {patient['allergies']}\n"
            if patient.get('status'):
                response += f"   📊 Status: {patient['status']}\n"
            if patient.get('assigned_at'):
                response += f"   📝 Admitted: {patient['assigned_at']}\n"
            if patient.get('discharged_at'):
                response += f"   📤 Discharged: {patient['discharged_at']}\n"
            
            response += "\n"
        
        if len(data) > 25:
            response += f"... and {len(data) - 25} more patients\n"
        
        return response
    
    def _format_room_data(self, data: List[Dict]) -> str:
        """Format room information"""
        response = "🏥 **Room Information:**\n\n"
        
        for room in data[:30]:
            room_num = room.get('room_number', 'Unknown')
            status = room.get('status', 'Unknown')
            
            response += f"**Room {room_num}** - {status}\n"
            response += f"   🏠 Type: {room.get('room_type', 'N/A')}\n"
            response += f"   🛏️ Capacity: {room.get('bed_capacity', 'N/A')} beds\n"
            
            if room.get('current_patient'):
                response += f"   👤 Patient: {room['current_patient']}\n"
                if room.get('assigned_at'):
                    response += f"   📅 Since: {room['assigned_at']}\n"
            
            response += "\n"
        
        return response
    
    def _format_staff_data(self, data: List[Dict]) -> str:
        """Format staff information"""
        response = "👨‍⚕️ **Staff Information:**\n\n"
        
        for staff in data:
            name = staff.get('staff_name', 'Unknown')
            role = staff.get('staff_type', staff.get('role', 'N/A'))
            
            response += f"**{name}** - {role}\n"
            if staff.get('email'):
                response += f"   📧 {staff['email']}\n"
            if staff.get('patients_assigned'):
                response += f"   👥 Patients Assigned: {staff['patients_assigned']}\n"
            response += "\n"
        
        return response
    
    def _format_equipment_data(self, data: List[Dict]) -> str:
        """Format equipment information"""
        response = "🔧 **Equipment Inventory:**\n\n"
        
        current_category = None
        for equipment in data:
            category = equipment.get('category', 'Other')
            if category != current_category:
                response += f"**{category}:**\n"
                current_category = category
            
            name = equipment.get('tool_name', 'Unknown')
            available = equipment.get('quantity_available', 0)
            total = equipment.get('quantity_total', 0)
            
            response += f"   • {name}: {available}/{total} available"
            
            if equipment.get('availability_percentage'):
                response += f" ({equipment['availability_percentage']}%)"
            
            if equipment.get('location_description'):
                response += f" - {equipment['location_description']}"
            
            response += "\n"
        
        return response
    
    def _format_statistics_data(self, data: List[Dict]) -> str:
        """Format statistics information"""
        response = "📊 **Hospital Statistics:**\n\n"
        
        for stat in data:
            metric = stat.get('metric', 'Unknown Metric')
            value = stat.get('value', 'N/A')
            unit = stat.get('unit', '')
            
            response += f"• **{metric}:** {value} {unit}\n"
        
        return response
    
    def _format_generic_data(self, data: List[Dict]) -> str:
        """Format generic data"""
        response = "📋 **Query Results:**\n\n"
        
        for i, record in enumerate(data[:10], 1):
            # Try to get a name for the record
            name = (record.get('full_name') or 
                   record.get('patient_name') or 
                   record.get('staff_name') or 
                   record.get('name') or 
                   f"Record {i}")
            
            response += f"**{name}:**\n"
            for key, value in record.items():
                if value is not None and key not in ['full_name', 'patient_name', 'staff_name', 'name']:
                    formatted_key = key.replace('_', ' ').title()
                    response += f"   • {formatted_key}: {value}\n"
            response += "\n"
        
        if len(data) > 10:
            response += f"... and {len(data) - 10} more records\n"
        
        return response
    
    def is_database_query(self, user_query: str) -> bool:
        """Check if the user query is a database-related query"""
        database_keywords = [
            'patient', 'patients', 'room', 'rooms', 'staff', 'doctor', 'nurse', 'nurses',
            'equipment', 'tools', 'medical', 'hospital', 'admission', 'discharge',
            'occupancy', 'inventory', 'statistics', 'total', 'count', 'list', 'top',
            'fetch', 'get', 'show', 'display', 'find', 'search', 'lookup', 'retrieve',
            'how many', 'who are', 'what is', 'where are', 'which', 'all the'
        ]
        
        user_query_lower = user_query.lower()
        return any(keyword in user_query_lower for keyword in database_keywords)

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