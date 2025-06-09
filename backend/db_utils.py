"""
Database utilities for connecting to Neon PostgreSQL and executing queries.
Replaces CSV file reading with direct database access.
"""
import os
import psycopg2
import pandas as pd
from typing import Optional, Dict, Any
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Try to import mock data for fallback
try:
    from .mock_data import mock_db
    MOCK_AVAILABLE = True
except ImportError:
    MOCK_AVAILABLE = False

class NeonDBConnection:
    """Handler for Neon PostgreSQL database connections."""
    
    def __init__(self):
        self.connection_params = {
            'host': os.getenv('NEON_HOST'),
            'database': os.getenv('NEON_DATABASE'),
            'user': os.getenv('NEON_USER'),
            'password': os.getenv('NEON_PASSWORD'),
            'port': os.getenv('NEON_PORT', '5432'),
            'sslmode': os.getenv('NEON_SSLMODE', 'require')
        }
        self._use_mock = False
        self._test_connection()
    
    def _test_connection(self):
        """Test database connection and fall back to mock if needed."""
        try:
            with self.get_connection() as conn:
                # Test with a simple query
                pd.read_sql_query("SELECT 1", conn)
                self._use_mock = False
                logger.info("Database connection successful")
        except Exception as e:
            if MOCK_AVAILABLE:
                logger.warning(f"Database connection failed: {e}. Using mock data.")
                self._use_mock = True
            else:
                logger.error(f"Database connection failed and no mock data available: {e}")
                raise

    @contextmanager
    def get_connection(self):
        """Get a database connection with automatic cleanup."""
        if self._use_mock:
            # For mock mode, we don't need a real connection
            yield None
            return
            
        conn = None
        try:
            conn = psycopg2.connect(**self.connection_params)
            yield conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
    
    def execute_query(self, query: str, params: tuple = None) -> pd.DataFrame:
        """Execute a query and return results as DataFrame."""
        if self._use_mock:
            return mock_db.execute_query(query, params)
        
        with self.get_connection() as conn:
            return pd.read_sql_query(query, conn, params=params)
    
    def get_rooms(self) -> pd.DataFrame:
        """Get rooms data from database."""
        if self._use_mock:
            return mock_db.get_rooms()
        
        query = """
        SELECT id, room_type, bed_capacity, status
        FROM rooms
        WHERE status = 'active'
        """
        return self.execute_query(query)
    
    def get_occupancy(self, days_back: int = 90) -> pd.DataFrame:
        """Get occupancy data from database."""
        if self._use_mock:
            return mock_db.get_occupancy(days_back)
        
        query = """
        SELECT o.id, o.room_id, o.patient_id, o.assigned_at, o.discharged_at, o.attendee
        FROM occupancy o
        WHERE o.assigned_at >= NOW() - INTERVAL '%s days'
        ORDER BY o.assigned_at DESC
        """
        df = self.execute_query(query, (days_back,))
        # Convert datetime columns
        df['assigned_at'] = pd.to_datetime(df['assigned_at'])
        df['discharged_at'] = pd.to_datetime(df['discharged_at'])
        return df
    
    def get_patient_records(self) -> pd.DataFrame:
        """Get patient records from database."""
        if self._use_mock:
            return mock_db.get_patient_records()
        
        query = """
        SELECT id, gender, date_of_birth, age_at_adm, 
               admission_reason, previous_visits
        FROM patient_records
        """
        df = self.execute_query(query)
        df['date_of_birth'] = pd.to_datetime(df['date_of_birth'])
        return df
    
    def get_users(self) -> pd.DataFrame:
        """Get users/staff data from database."""
        if self._use_mock:
            return mock_db.get_users()
        
        query = """
        SELECT id, full_name, staff_type, department, shift_pattern
        FROM users
        WHERE status = 'active'
        """
        return self.execute_query(query)
    
    def get_tools(self) -> pd.DataFrame:
        """Get tools/equipment data from database."""
        if self._use_mock:
            return mock_db.get_tools()
        
        query = """
        SELECT id, tool_name, quantity_total, quantity_available, 
               quantity_in_use, maintenance_status
        FROM tools
        WHERE status = 'active'
        """
        return self.execute_query(query)
    
    def get_inventory(self) -> pd.DataFrame:
        """Get hospital inventory data from database."""
        if self._use_mock:
            return mock_db.get_inventory()
        
        query = """
        SELECT id, item_name, category, quantity_available, 
               expiry_date, supplier, unit_cost
        FROM hospital_inventory
        WHERE status = 'active'
        """
        df = self.execute_query(query)
        df['expiry_date'] = pd.to_datetime(df['expiry_date'])
        return df

# Global database instance
db = NeonDBConnection() 