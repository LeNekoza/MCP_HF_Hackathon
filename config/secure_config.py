"""
Secure Database Configuration Loader
This module provides secure loading of database configuration from environment variables.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from utils.env_loader import ensure_env_loaded

    ensure_env_loaded()
except ImportError:
    # Fallback if env_loader is not available
    pass


def load_database_config() -> Dict[str, Any]:
    """
    Load database configuration from environment variables.

    Returns:
        Dict containing database configuration

    Raises:
        ValueError: If required configuration is missing
    """
    # Load from environment variables
    required_vars = ["NEON_HOST", "NEON_DATABASE", "NEON_USER", "NEON_PASSWORD"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        raise ValueError(
            f"Database configuration missing required environment variables: {', '.join(missing_vars)}\n"
            "Please set the following environment variables:\n"
            "- NEON_HOST: Your Neon database host\n"
            "- NEON_DATABASE: Database name\n"
            "- NEON_USER: Database username\n"
            "- NEON_PASSWORD: Database password\n"
            "Optional variables:\n"
            "- NEON_PORT: Database port (default: 5432)\n"
            "- NEON_SSLMODE: SSL mode (default: require)\n"
            "- CLEAR_EXISTING_DATA: Clear data on upload (default: true)\n"
            "- BATCH_SIZE: Batch size for uploads (default: 1000)\n"
            "- LOG_LEVEL: Logging level (default: INFO)"
        )

    return {
        "database": {
            "host": os.getenv("NEON_HOST"),
            "database": os.getenv("NEON_DATABASE"),
            "user": os.getenv("NEON_USER"),
            "password": os.getenv("NEON_PASSWORD"),
            "port": int(os.getenv("NEON_PORT", "5432")),
            "sslmode": os.getenv("NEON_SSLMODE", "require"),
        },
        "upload_settings": {
            "clear_existing_data": os.getenv("CLEAR_EXISTING_DATA", "true").lower()
            == "true",
            "batch_size": int(os.getenv("BATCH_SIZE", "1000")),
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
        },
    }


def get_connection_string() -> str:
    """
    Generate PostgreSQL connection string from configuration.

    Returns:
        PostgreSQL connection string
    """
    config = load_database_config()
    db = config["database"]

    return (
        f"postgresql://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['database']}"
        f"?sslmode={db['sslmode']}"
    )


if __name__ == "__main__":
    # Test configuration loading
    try:
        config = load_database_config()
        print("✅ Database configuration loaded successfully")
        print(f"Host: {config['database']['host']}")
        print(f"Database: {config['database']['database']}")
        print(f"User: {config['database']['user']}")
        print("Password: [HIDDEN]")
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
