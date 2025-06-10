import psycopg2
import psycopg2.extras
from typing import Dict, List, Any, Optional
import json
import logging
from datetime import datetime
import os


class DatabaseService:
    """Database service for hospital management system using PostgreSQL"""

    def __init__(self):
        self.connection = None
        self.logger = logging.getLogger(__name__)

    def connect(self) -> bool:
        """Establish connection to PostgreSQL database"""
        try:
            # Get database connection parameters from environment variables
            db_config = {
                "host": os.getenv("NEON_HOST", "localhost"),
                "port": os.getenv("NEON_PORT", "5432"),
                "database": os.getenv("NEON_DATABASE", "hospital_db"),
                "user": os.getenv("NEON_USER", "postgres"),
                "password": os.getenv("NEON_PASSWORD", "password"),
            }

            self.connection = psycopg2.connect(**db_config)
            self.connection.autocommit = True
            self.logger.info("Database connection established successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to connect to database: {str(e)}")
            return False

    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.logger.info("Database connection closed")

    def execute_query(self, query: str, params: tuple = None) -> Optional[List[Dict]]:
        """Execute a SELECT query and return results as list of dictionaries"""
        try:
            if not self.connection:
                if not self.connect():
                    return None

            with self.connection.cursor(
                cursor_factory=psycopg2.extras.RealDictCursor
            ) as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()
                return [dict(row) for row in results]

        except Exception as e:
            self.logger.error(f"Query execution failed: {str(e)}")
            return None

    def execute_update(self, query: str, params: tuple = None) -> bool:
        """Execute an INSERT, UPDATE, or DELETE query"""
        try:
            if not self.connection:
                if not self.connect():
                    return False

            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                return True

        except Exception as e:
            self.logger.error(f"Update execution failed: {str(e)}")
            return False

    # Table-specific methods
    def get_patients(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get patient records with user information"""
        query = """
        SELECT 
            pr.id,
            u.full_name,
            pr.date_of_birth,
            pr.gender,
            pr.blood_group,
            pr.allergies,
            u.phone_number,
            CASE 
                WHEN o.patient_id IS NOT NULL THEN 'Active'
                ELSE 'Discharged'
            END as status,
            r.room_number
        FROM patient_records pr
        LEFT JOIN users u ON pr.user_id = u.id
        LEFT JOIN occupancy o ON pr.id = o.patient_id AND o.discharged_at IS NULL
        LEFT JOIN rooms r ON o.room_id = r.id
        ORDER BY pr.id
        LIMIT %s OFFSET %s
        """
        return self.execute_query(query, (limit, offset)) or []

    def get_patients_count(self) -> int:
        """Get total count of patients"""
        query = "SELECT COUNT(*) as count FROM patient_records"
        result = self.execute_query(query)
        return result[0]["count"] if result else 0

    def get_staff(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get staff members"""
        query = """
        SELECT 
            id,
            full_name,
            email,
            role,
            staff_type,
            phone_number
        FROM users
        WHERE role IN ('doctor', 'nurse', 'admin', 'technician')
        ORDER BY full_name
        LIMIT %s OFFSET %s
        """
        return self.execute_query(query, (limit, offset)) or []

    def get_staff_count(self) -> int:
        """Get total count of staff"""
        query = "SELECT COUNT(*) as count FROM users WHERE role IN ('doctor', 'nurse', 'admin', 'technician')"
        result = self.execute_query(query)
        return result[0]["count"] if result else 0

    def get_rooms(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get room information with occupancy status"""
        query = """
        SELECT 
            r.id,
            r.room_number,
            r.room_type,
            r.bed_capacity,
            r.floor_number,
            COUNT(o.id) as current_occupancy,
            CASE 
                WHEN COUNT(o.id) >= r.bed_capacity THEN 'Full'
                WHEN COUNT(o.id) = 0 THEN 'Empty'
                ELSE 'Available'
            END as status
        FROM rooms r
        LEFT JOIN occupancy o ON r.id = o.room_id AND o.discharged_at IS NULL
        GROUP BY r.id, r.room_number, r.room_type, r.bed_capacity, r.floor_number
        ORDER BY r.room_number
        LIMIT %s OFFSET %s
        """
        return self.execute_query(query, (limit, offset)) or []

    def get_rooms_count(self) -> int:
        """Get total count of rooms"""
        query = "SELECT COUNT(*) as count FROM rooms"
        result = self.execute_query(query)
        return result[0]["count"] if result else 0

    def get_equipment(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get equipment/tools information"""
        query = """
        SELECT 
            t.id,
            t.tool_name as equipment,
            t.category,
            t.quantity_total,
            t.quantity_available,
            t.location_description as location,
            CASE 
                WHEN t.quantity_available > 0 THEN 'Available'
                ELSE 'Out of Stock'
            END as status
        FROM tools t
        ORDER BY t.tool_name
        LIMIT %s OFFSET %s
        """
        return self.execute_query(query, (limit, offset)) or []

    def get_equipment_count(self) -> int:
        """Get total count of equipment"""
        query = "SELECT COUNT(*) as count FROM tools"
        result = self.execute_query(query)
        return result[0]["count"] if result else 0

    def get_inventory(self, limit: int = 100) -> List[Dict]:
        """Get hospital inventory with expiry information"""
        query = """
        SELECT 
            hi.id,
            hi.item_name,
            hi.item_type,
            hi.quantity_available,
            hi.location_description,
            hi.expiry_date,
            CASE 
                WHEN hi.expiry_date < CURRENT_DATE THEN 'Expired'
                WHEN hi.expiry_date < CURRENT_DATE + INTERVAL '30 days' THEN 'Expiring Soon'
                WHEN hi.quantity_available = 0 THEN 'Out of Stock'
                ELSE 'Available'
            END as status
        FROM hospital_inventory hi
        ORDER BY hi.expiry_date ASC NULLS LAST
        LIMIT %s
        """
        return self.execute_query(query, (limit,)) or []

    def update_patient(self, patient_id: int, data: Dict) -> bool:
        """Update patient record"""
        query = """
        UPDATE patient_records 
        SET date_of_birth = %s, gender = %s, blood_group = %s, allergies = %s
        WHERE id = %s
        """
        params = (
            data.get("date_of_birth"),
            data.get("gender"),
            data.get("blood_group"),
            data.get("allergies"),
            patient_id,
        )
        return self.execute_update(query, params)

    def delete_patient(self, patient_id: int) -> bool:
        """Delete patient record (soft delete by updating discharge date)"""
        query = """
        UPDATE occupancy 
        SET discharged_at = CURRENT_TIMESTAMP 
        WHERE patient_id = %s AND discharged_at IS NULL
        """
        return self.execute_update(query, (patient_id,))

    def update_room(self, room_id: int, data: Dict) -> bool:
        """Update room information"""
        query = """
        UPDATE rooms 
        SET room_type = %s, bed_capacity = %s, floor_number = %s, notes = %s
        WHERE id = %s
        """
        params = (
            data.get("room_type"),
            data.get("bed_capacity"),
            data.get("floor_number"),
            data.get("notes"),
            room_id,
        )
        return self.execute_update(query, params)

    def update_equipment(self, equipment_id: int, data: Dict) -> bool:
        """Update equipment/tool information"""
        query = """
        UPDATE tools 
        SET quantity_available = %s, location_description = %s
        WHERE id = %s
        """
        params = (
            data.get("quantity_available"),
            data.get("location_description"),
            equipment_id,
        )
        return self.execute_update(query, params)

    def get_dashboard_stats(self) -> Dict:
        """Get dashboard statistics"""
        stats = {}

        # Patient statistics
        patient_stats = self.execute_query(
            """
            SELECT 
                COUNT(*) as total_patients,
                COUNT(CASE WHEN o.discharged_at IS NULL THEN 1 END) as active_patients
            FROM patient_records pr
            LEFT JOIN occupancy o ON pr.id = o.patient_id
        """
        )

        # Room occupancy statistics
        room_stats = self.execute_query(
            """
            SELECT 
                COUNT(*) as total_rooms,
                SUM(bed_capacity) as total_beds,
                COUNT(CASE WHEN o.discharged_at IS NULL THEN 1 END) as occupied_beds
            FROM rooms r
            LEFT JOIN occupancy o ON r.id = o.room_id
        """
        )

        # Staff statistics
        staff_stats = self.execute_query(
            """
            SELECT 
                COUNT(*) as total_staff,
                COUNT(CASE WHEN role = 'doctor' THEN 1 END) as total_doctors,
                COUNT(CASE WHEN role = 'nurse' THEN 1 END) as total_nurses
            FROM users
            WHERE role IN ('doctor', 'nurse', 'admin', 'technician')
        """
        )

        if patient_stats:
            stats.update(patient_stats[0])
        if room_stats:
            stats.update(room_stats[0])
        if staff_stats:
            stats.update(staff_stats[0])

        return stats

    def get_recent_admissions(self, limit: int = 10) -> List[Dict]:
        """Get recent patient admissions"""
        query = """
        SELECT 
            u.full_name,
            pr.id as patient_id,
            r.room_number,
            o.assigned_at,
            pr.blood_group
        FROM occupancy o
        JOIN patient_records pr ON o.patient_id = pr.id
        JOIN users u ON pr.user_id = u.id
        JOIN rooms r ON o.room_id = r.id
        WHERE o.discharged_at IS NULL
        ORDER BY o.assigned_at DESC
        LIMIT %s
        """
        return self.execute_query(query, (limit,)) or []

    def search_patients(self, search_term: str) -> List[Dict]:
        """Search patients by name or ID"""
        query = """
        SELECT 
            pr.id,
            u.full_name,
            pr.date_of_birth,
            pr.gender,
            pr.blood_group,
            CASE 
                WHEN o.patient_id IS NOT NULL THEN 'Active'
                ELSE 'Discharged'
            END as status,
            r.room_number
        FROM patient_records pr
        LEFT JOIN users u ON pr.user_id = u.id
        LEFT JOIN occupancy o ON pr.id = o.patient_id AND o.discharged_at IS NULL
        LEFT JOIN rooms r ON o.room_id = r.id
        WHERE u.full_name ILIKE %s OR pr.id::text = %s
        ORDER BY pr.id
        """
        search_pattern = f"%{search_term}%"
        return self.execute_query(query, (search_pattern, search_term)) or []

    # Individual record retrieval methods for editing
    def get_patient_by_id(self, patient_id: int) -> Optional[Dict]:
        """Get a single patient record by ID"""
        query = """
        SELECT 
            pr.id,
            u.full_name,
            pr.date_of_birth,
            pr.gender,
            pr.blood_group,
            pr.allergies,
            u.phone_number,
            CASE 
                WHEN o.patient_id IS NOT NULL THEN 'Active'
                ELSE 'Discharged'
            END as status,
            r.room_number
        FROM patient_records pr
        LEFT JOIN users u ON pr.user_id = u.id
        LEFT JOIN occupancy o ON pr.id = o.patient_id AND o.discharged_at IS NULL
        LEFT JOIN rooms r ON o.room_id = r.id
        WHERE pr.id = %s
        """
        result = self.execute_query(query, (patient_id,))
        return result[0] if result else None

    def get_staff_by_id(self, staff_id: int) -> Optional[Dict]:
        """Get a single staff member by ID"""
        query = """
        SELECT 
            id,
            full_name,
            email,
            role,
            staff_type,
            phone_number
        FROM users
        WHERE id = %s AND role IN ('doctor', 'nurse', 'admin', 'technician')
        """
        result = self.execute_query(query, (staff_id,))
        return result[0] if result else None

    def get_room_by_id(self, room_id: int) -> Optional[Dict]:
        """Get a single room by ID"""
        query = """
        SELECT 
            r.id,
            r.room_number,
            r.room_type,
            r.bed_capacity,
            r.floor_number,
            r.notes,
            COUNT(o.id) as current_occupancy,
            CASE 
                WHEN COUNT(o.id) >= r.bed_capacity THEN 'Full'
                WHEN COUNT(o.id) = 0 THEN 'Empty'
                ELSE 'Available'
            END as status
        FROM rooms r
        LEFT JOIN occupancy o ON r.id = o.room_id AND o.discharged_at IS NULL
        WHERE r.id = %s
        GROUP BY r.id, r.room_number, r.room_type, r.bed_capacity, r.floor_number, r.notes
        """
        result = self.execute_query(query, (room_id,))
        return result[0] if result else None

    def get_equipment_by_id(self, equipment_id: int) -> Optional[Dict]:
        """Get a single equipment item by ID"""
        query = """
        SELECT 
            t.id,
            t.tool_name as equipment,
            t.category,
            t.quantity_total,
            t.quantity_available,
            t.location_description as location,
            CASE 
                WHEN t.quantity_available > 0 THEN 'Available'
                ELSE 'Out of Stock'
            END as status
        FROM tools t
        WHERE t.id = %s
        """
        result = self.execute_query(query, (equipment_id,))
        return result[0] if result else None

    # Additional update method for staff
    def update_staff(self, staff_id: int, data: Dict) -> bool:
        """Update staff member information"""
        query = """
        UPDATE users 
        SET full_name = %s, email = %s, role = %s, staff_type = %s, phone_number = %s
        WHERE id = %s AND role IN ('doctor', 'nurse', 'admin', 'technician')
        """
        params = (
            data.get("full_name"),
            data.get("email"),
            data.get("role"),
            data.get("staff_type"),
            data.get("phone_number"),
            staff_id,
        )
        return self.execute_update(query, params)


# Global instance
db_service = DatabaseService()
