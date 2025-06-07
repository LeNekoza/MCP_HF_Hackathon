"""
Hospital Schema Context Loader
Loads and formats the hospital schema guide for use in AI prompts
"""

import os
from pathlib import Path
from typing import Optional
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class HospitalSchemaLoader:
    """Utility class to load and format hospital schema information for AI context"""

    def __init__(self):
        """Initialize the schema loader"""
        self.schema_content: Optional[str] = None
        self._load_schema_guide()

    def _load_schema_guide(self) -> None:
        """Load the hospital schema guide from the data directory"""
        try:
            # Get the project root directory
            project_root = Path(__file__).parent.parent.parent
            schema_path = project_root / "data" / "hospital_schema_guide.md"

            if not schema_path.exists():
                logger.warning(f"Hospital schema guide not found at {schema_path}")
                self.schema_content = self._get_fallback_schema()
                return

            with open(schema_path, "r", encoding="utf-8") as f:
                self.schema_content = f.read()

            logger.info("Hospital schema guide loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load hospital schema guide: {e}")
            self.schema_content = self._get_fallback_schema()

    def _get_fallback_schema(self) -> str:
        """Provide a basic fallback schema if the guide file is not available"""
        return """
        # Basic Hospital Schema

        ## Tables:
        - users: id, full_name, email, role (patient/staff/admin), staff_type
        - patient_records: id, user_id, date_of_birth, gender, blood_group, allergies, medical_history
        - rooms: id, room_number, room_type, bed_capacity, floor_number
        - occupancy: id, patient_id, room_id, assigned_at, discharged_at
        - tools: id, tool_name, category, quantity_total, quantity_available
        - storage_rooms: id, storage_number, storage_type, floor_number
        - hospital_inventory: id, item_name, item_type, quantity_total, quantity_available

        ## Key Relationships:
        - users.id = patient_records.user_id
        - occupancy.patient_id = patient_records.id
        - occupancy.room_id = rooms.id
        """

    def get_sql_context(self) -> str:
        """Get formatted schema context for SQL generation"""
        if not self.schema_content:
            return self._get_fallback_schema()

        # Extract relevant sections for SQL generation
        sql_context = f"""
HOSPITAL DATABASE SCHEMA CONTEXT:

{self.schema_content}

IMPORTANT SQL GENERATION RULES:
1. For blood group queries, use patient_records.blood_group (patient blood types)
2. For blood inventory queries, use hospital_inventory with item_type='blood_unit'
3. Always use proper JOINs when data spans multiple tables
4. Use meaningful table aliases (u for users, pr for patient_records, etc.)
5. Filter by role='patient' when querying patient data from users table
6. Use LEFT JOINs for optional relationships (like current room assignments)
7. Order results logically and include appropriate LIMIT clauses
"""
        return sql_context

    def get_medical_context(self) -> str:
        """Get formatted schema context for general medical queries"""
        if not self.schema_content:
            return "Basic hospital database available."

        return f"""
HOSPITAL DATA CONTEXT:

{self.schema_content}

This context helps you understand the hospital's data structure when answering questions about:
- Patient information and medical records
- Room assignments and availability
- Medical equipment and inventory
- Staff information
- Hospital statistics and reports
"""

    def get_interpretation_rules(self) -> str:
        """Get the interpretation rules section from the schema guide"""
        if not self.schema_content:
            return "Use standard medical interpretations."

        # Try to extract the interpretation rules section
        content = self.schema_content

        # Look for the interpretation rules section
        rules_start = content.find("## 4. Query Interpretation Rules")
        if rules_start == -1:
            return "Apply medical domain knowledge for query interpretation."

        rules_end = content.find("## 5.", rules_start)
        if rules_end == -1:
            rules_end = content.find("---", rules_start)
            if rules_end == -1:
                rules_end = len(content)

        rules_section = content[rules_start:rules_end].strip()

        return f"""
QUERY INTERPRETATION RULES:

{rules_section}
"""

    def reload_schema(self) -> bool:
        """Reload the schema guide from file"""
        try:
            self._load_schema_guide()
            return True
        except Exception as e:
            logger.error(f"Failed to reload schema: {e}")
            return False

    def is_schema_available(self) -> bool:
        """Check if schema content is available"""
        return self.schema_content is not None and len(self.schema_content.strip()) > 0


# Global instance for easy access
hospital_schema_loader = HospitalSchemaLoader()
