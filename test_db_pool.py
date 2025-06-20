"""
Test script for database connection pool implementation
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.services.db_pool import get_db_pool, get_db_connection
from src.services.database_service import DatabaseService
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_db_pool():
    """Test the database connection pool"""
    logger.info("Testing database connection pool...")
    
    try:
        # Test pool initialization
        pool = get_db_pool()
        logger.info("✅ Database pool initialized successfully")
        
        # Test getting connection from pool
        with get_db_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            logger.info(f"✅ Connection test successful: {result}")
            cursor.close()
        
        # Test database service
        db_service = DatabaseService()
        result = db_service.execute_query("SELECT 1 as test")
        logger.info(f"✅ Database service test successful: {result}")
        
        logger.info("🎉 All tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False
    
    finally:
        # Clean up pool
        try:
            pool.close_all_connections()
            logger.info("✅ Pool connections closed")
        except:
            pass

if __name__ == "__main__":
    test_db_pool()
