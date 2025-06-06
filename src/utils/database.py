"""
Database utilities for NeonDB PostgreSQL integration
Provides functions for connecting to and retrieving data from the hospital database
"""

import psycopg2
import pandas as pd
from typing import Dict, List, Any, Optional
import logging
from contextlib import contextmanager

from .logger import setup_logger

# Import from root directory secure_config
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from secure_config import load_database_config, get_connection_string

logger = setup_logger()


class DatabaseConnection:
    """Database connection manager for NeonDB PostgreSQL"""
    
    def __init__(self):
        """Initialize database connection with configuration"""
        self.config = load_database_config()
        self.connection_string = get_connection_string()
        logger.info("Database connection initialized")
    
    @contextmanager
    def get_connection(self):
        """Get a database connection with automatic cleanup"""
        conn = None
        try:
            conn = psycopg2.connect(self.connection_string)
            yield conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
    
    def test_connection(self) -> bool:
        """Test database connectivity"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                cursor.close()
                logger.info("Database connection test successful")
                return result[0] == 1
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False


class HospitalDataRetriever:
    """Data retrieval operations for hospital database"""
    
    def __init__(self):
        """Initialize data retriever with database connection"""
        self.db = DatabaseConnection()
    
    def get_all_users(self, limit: Optional[int] = None) -> pd.DataFrame:
        """Retrieve all users from the database"""
        query = "SELECT * FROM users"
        if limit:
            query += f" LIMIT {limit}"
        
        try:
            with self.db.get_connection() as conn:
                df = pd.read_sql_query(query, conn)
                logger.info(f"Retrieved {len(df)} users from database")
                return df
        except Exception as e:
            logger.error(f"Error retrieving users: {e}")
            return pd.DataFrame()
    
    def get_patients(self, limit: Optional[int] = None) -> pd.DataFrame:
        """Retrieve patient records with user information"""
        query = """
        SELECT 
            u.id, u.full_name, u.email, u.phone_number,
            pr.date_of_birth, pr.gender, pr.blood_group, 
            pr.allergies, pr.medical_history, pr.emergency_contact
        FROM users u
        JOIN patient_records pr ON u.id = pr.user_id
        WHERE u.role = 'patient'
        """
        if limit:
            query += f" LIMIT {limit}"
        
        try:
            with self.db.get_connection() as conn:
                df = pd.read_sql_query(query, conn)
                logger.info(f"Retrieved {len(df)} patient records from database")
                return df
        except Exception as e:
            logger.error(f"Error retrieving patients: {e}")
            return pd.DataFrame()
    
    def get_staff(self, staff_type: Optional[str] = None, limit: Optional[int] = None) -> pd.DataFrame:
        """Retrieve staff members, optionally filtered by staff type"""
        query = """
        SELECT id, full_name, email, phone_number, role, staff_type
        FROM users 
        WHERE role IN ('staff', 'doctor', 'nurse', 'admin')
        """
        
        if staff_type:
            query += f" AND staff_type = '{staff_type}'"
        
        if limit:
            query += f" LIMIT {limit}"
        
        try:
            with self.db.get_connection() as conn:
                df = pd.read_sql_query(query, conn)
                logger.info(f"Retrieved {len(df)} staff records from database")
                return df
        except Exception as e:
            logger.error(f"Error retrieving staff: {e}")
            return pd.DataFrame()
    
    def get_rooms(self, room_type: Optional[str] = None, available_only: bool = False, limit: Optional[int] = None) -> pd.DataFrame:
        """Retrieve room information, optionally filtered by type and availability"""
        if available_only:
            query = """
            SELECT r.*, 
                   CASE WHEN o.room_id IS NULL THEN true ELSE false END as available
            FROM rooms r
            LEFT JOIN occupancy o ON r.id = o.room_id AND o.discharged_at IS NULL
            WHERE o.room_id IS NULL
            """
        else:
            query = """
            SELECT r.*, 
                   CASE WHEN o.room_id IS NULL THEN true ELSE false END as available
            FROM rooms r
            LEFT JOIN occupancy o ON r.id = o.room_id AND o.discharged_at IS NULL
            """
        
        if room_type:
            query += f" AND r.room_type = '{room_type}'"
        
        if limit:
            query += f" LIMIT {limit}"
        
        try:
            with self.db.get_connection() as conn:
                df = pd.read_sql_query(query, conn)
                logger.info(f"Retrieved {len(df)} room records from database")
                return df
        except Exception as e:
            logger.error(f"Error retrieving rooms: {e}")
            return pd.DataFrame()
    
    def get_occupancy(self, active_only: bool = True) -> pd.DataFrame:
        """Retrieve occupancy information with patient and room details"""
        query = """
        SELECT 
            o.id, o.bed_number, o.assigned_at, o.discharged_at,
            u.full_name as patient_name,
            r.room_number, r.room_type
        FROM occupancy o
        JOIN patient_records pr ON o.patient_id = pr.id
        JOIN users u ON pr.user_id = u.id
        JOIN rooms r ON o.room_id = r.id
        """
        
        if active_only:
            query += " WHERE o.discharged_at IS NULL"
        
        try:
            with self.db.get_connection() as conn:
                df = pd.read_sql_query(query, conn)
                logger.info(f"Retrieved {len(df)} occupancy records from database")
                return df
        except Exception as e:
            logger.error(f"Error retrieving occupancy: {e}")
            return pd.DataFrame()
    
    def get_medical_equipment(self, location_id: Optional[int] = None, available_only: bool = False, limit: Optional[int] = None) -> pd.DataFrame:
        """Retrieve medical tools and equipment"""
        query = """
        SELECT 
            t.id, t.tool_name, t.description, t.category,
            t.quantity_total, t.quantity_available, t.location_description,
            sr.storage_number, sr.storage_type
        FROM tools t
        LEFT JOIN storage_rooms sr ON t.location_storage_id = sr.id
        """
        
        conditions = []
        if location_id:
            conditions.append(f"t.location_storage_id = {location_id}")
        if available_only:
            conditions.append("t.quantity_available > 0")
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        if limit:
            query += f" LIMIT {limit}"
        
        try:
            with self.db.get_connection() as conn:
                df = pd.read_sql_query(query, conn)
                logger.info(f"Retrieved {len(df)} medical equipment records from database")
                return df
        except Exception as e:
            logger.error(f"Error retrieving medical equipment: {e}")
            return pd.DataFrame()
    
    def get_hospital_inventory(self, location_id: Optional[int] = None, item_type: Optional[str] = None) -> pd.DataFrame:
        """Retrieve hospital inventory"""
        query = """
        SELECT 
            hi.id, hi.item_name, hi.item_type, hi.quantity_total, 
            hi.quantity_available, hi.location_description, hi.details, hi.expiry_date,
            sr.storage_number, sr.storage_type
        FROM hospital_inventory hi
        LEFT JOIN storage_rooms sr ON hi.location_storage_id = sr.id
        """
        
        conditions = []
        if location_id:
            conditions.append(f"hi.location_storage_id = {location_id}")
        if item_type:
            conditions.append(f"hi.item_type = '{item_type}'")
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        try:
            with self.db.get_connection() as conn:
                df = pd.read_sql_query(query, conn)
                logger.info(f"Retrieved {len(df)} inventory records from database")
                return df
        except Exception as e:
            logger.error(f"Error retrieving inventory: {e}")
            return pd.DataFrame()
    
    def get_storage_rooms(self, floor_number: Optional[int] = None) -> pd.DataFrame:
        """Retrieve storage room information"""
        query = "SELECT * FROM storage_rooms"
        
        if floor_number:
            query += f" WHERE floor_number = {floor_number}"
        
        try:
            with self.db.get_connection() as conn:
                df = pd.read_sql_query(query, conn)
                logger.info(f"Retrieved {len(df)} storage room records from database")
                return df
        except Exception as e:
            logger.error(f"Error retrieving storage rooms: {e}")
            return pd.DataFrame()
    
    def search_patients_by_name(self, name_pattern: str) -> pd.DataFrame:
        """Search patients by name pattern"""
        query = """
        SELECT 
            u.id, u.full_name, u.email, u.phone_number,
            pr.date_of_birth, pr.gender, pr.blood_group
        FROM users u
        JOIN patient_records pr ON u.id = pr.user_id
        WHERE u.role = 'patient' AND u.full_name ILIKE %s
        """
        
        try:
            with self.db.get_connection() as conn:
                df = pd.read_sql_query(query, conn, params=[f"%{name_pattern}%"])
                logger.info(f"Found {len(df)} patients matching '{name_pattern}'")
                return df
        except Exception as e:
            logger.error(f"Error searching patients: {e}")
            return pd.DataFrame()
    
    def get_database_stats(self) -> Dict[str, int]:
        """Get database statistics (record counts for each table)"""
        tables = ['users', 'patient_records', 'rooms', 'occupancy', 
                 'tools', 'hospital_inventory', 'storage_rooms']
        stats = {}
        
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    stats[table] = count
                cursor.close()
                logger.info("Retrieved database statistics")
                return stats
        except Exception as e:
            logger.error(f"Error retrieving database stats: {e}")
            return {}


# Convenience functions for easy import
def get_data_retriever() -> HospitalDataRetriever:
    """Get a configured data retriever instance"""
    return HospitalDataRetriever()

def test_database_connection() -> bool:
    """Test database connectivity"""
    db = DatabaseConnection()
    return db.test_connection() 