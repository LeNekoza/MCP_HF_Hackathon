"""
Database connection and utilities for Neon DB
"""
import os
import pandas as pd
import psycopg2
from typing import Optional
import logging
from contextlib import contextmanager

# Load environment variables
try:
    from src.utils.env_loader import ensure_env_loaded
    ensure_env_loaded()
except ImportError:
    # Fallback if env_loader not available
    from dotenv import load_dotenv
    load_dotenv()

logger = logging.getLogger(__name__)

class NeonDBConnection:
    """Handles connection to Neon PostgreSQL database"""
    
    def __init__(self):
        self.host = os.getenv("NEON_HOST")
        self.database = os.getenv("NEON_DATABASE") 
        self.user = os.getenv("NEON_USER")
        self.password = os.getenv("NEON_PASSWORD")
        self.port = os.getenv("NEON_PORT", "5432")
        self.sslmode = os.getenv("NEON_SSLMODE", "require")
        
    def get_connection_string(self) -> str:
        """Returns the database connection string"""
        return (
            f"postgresql://{self.user}:{self.password}@{self.host}:"
            f"{self.port}/{self.database}?sslmode={self.sslmode}"
        )
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port,
                sslmode=self.sslmode
            )
            yield conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
    
    def read_sql(self, query: str) -> pd.DataFrame:
        """Execute SQL query and return DataFrame"""
        try:
            # Use SQLAlchemy engine for better pandas compatibility
            from sqlalchemy import create_engine
            engine = create_engine(self.get_connection_string())
            return pd.read_sql(query, engine)
        except Exception as e:
            logger.error(f"SQL query error: {e}")
            raise

# Global instance
db = NeonDBConnection()

def get_rooms() -> pd.DataFrame:
    """Load rooms data from database"""
    query = "SELECT * FROM rooms"
    return db.read_sql(query)

def get_occupancy() -> pd.DataFrame:
    """Load occupancy data from database"""
    query = "SELECT * FROM occupancy"
    df = db.read_sql(query)
    # Convert datetime columns
    if 'assigned_at' in df.columns:
        df['assigned_at'] = pd.to_datetime(df['assigned_at'])
    if 'discharged_at' in df.columns:
        df['discharged_at'] = pd.to_datetime(df['discharged_at'])
    return df

def get_patients() -> pd.DataFrame:
    """Load patient records from database"""
    query = "SELECT * FROM patient_records"
    df = db.read_sql(query)
    if 'date_of_birth' in df.columns:
        df['date_of_birth'] = pd.to_datetime(df['date_of_birth'])
    return df

def get_users() -> pd.DataFrame:
    """Load users data from database"""
    query = "SELECT * FROM users"
    return db.read_sql(query)

def get_tools() -> pd.DataFrame:
    """Load tools data from database"""
    query = "SELECT * FROM tools"
    return db.read_sql(query)

def get_inventory() -> pd.DataFrame:
    """Load hospital inventory from database"""
    query = "SELECT * FROM hospital_inventory"
    df = db.read_sql(query)
    if 'expiry_date' in df.columns:
        df['expiry_date'] = pd.to_datetime(df['expiry_date'])
    return df 