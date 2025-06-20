"""
Database Connection Pool Service
Provides a psycopg2 connection pool for efficient database connection management.
"""

import logging
from typing import Optional
import psycopg2.pool
from contextlib import contextmanager
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from config.secure_config import load_database_config

logger = logging.getLogger(__name__)


class DatabasePool:
    """Singleton database connection pool manager"""
    
    _instance = None
    _pool = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabasePool, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._pool is None:
            self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize the connection pool"""
        try:
            config = load_database_config()
            db_config = config["database"]
            
            # Create connection pool with minimum 1 and maximum 10 connections
            self._pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                host=db_config["host"],
                port=db_config["port"],
                database=db_config["database"],
                user=db_config["user"],
                password=db_config["password"],
                sslmode=db_config["sslmode"]
            )
            
            logger.info("Database connection pool initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database connection pool: {e}")
            raise RuntimeError(f"Database pool initialization failed: {e}")
    
    def get_connection(self):
        """Get a connection from the pool"""
        if self._pool is None:
            raise RuntimeError("Database pool not initialized")
        
        try:
            connection = self._pool.getconn()
            if connection is None:
                raise RuntimeError("Failed to get connection from pool")
            
            # Set autocommit to True for compatibility with existing code
            connection.autocommit = True
            return connection
            
        except Exception as e:
            logger.error(f"Failed to get connection from pool: {e}")
            raise RuntimeError(f"Failed to get database connection: {e}")
    
    def return_connection(self, connection):
        """Return a connection to the pool"""
        if self._pool is None:
            logger.warning("Attempting to return connection to uninitialized pool")
            return
        
        try:
            self._pool.putconn(connection)
        except Exception as e:
            logger.error(f"Failed to return connection to pool: {e}")
    
    def close_all_connections(self):
        """Close all connections in the pool"""
        if self._pool is not None:
            try:
                self._pool.closeall()
                logger.info("All database connections closed")
            except Exception as e:
                logger.error(f"Error closing database connections: {e}")
            finally:
                self._pool = None


# Global instance
_db_pool = None


def get_db_pool() -> DatabasePool:
    """Get the global database pool instance"""
    global _db_pool
    if _db_pool is None:
        _db_pool = DatabasePool()
    return _db_pool


@contextmanager
def get_db_connection():
    """Context manager for getting and returning database connections"""
    pool = get_db_pool()
    connection = None
    
    try:
        connection = pool.get_connection()
        yield connection
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise
    finally:
        if connection is not None:
            pool.return_connection(connection)
