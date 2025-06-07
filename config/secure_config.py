"""
Secure Database Configuration Loader
This module provides secure loading of database configuration from environment variables.
"""

import os
import json
from typing import Dict, Any


def load_database_config() -> Dict[str, Any]:
    """
    Load database configuration from environment variables.
    Falls back to neon_config.json if environment variables are not set.

    Returns:
        Dict containing database configuration

    Raises:
        ValueError: If required configuration is missing
    """
    # Try to load from environment variables first (more secure)
    if all(
        os.getenv(key)
        for key in ["NEON_HOST", "NEON_DATABASE", "NEON_USER", "NEON_PASSWORD"]
    ):
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

    # Fallback to config file (less secure, for development only)
    try:
        config_path = os.path.join(os.path.dirname(__file__), "neon_config.json")
        with open(config_path, "r") as f:
            config = json.load(f)
            print(
                "WARNING: Using neon_config.json file. Consider using environment variables for production."
            )
            return config
    except FileNotFoundError:
        raise ValueError(
            "Database configuration not found. Either:\n"
            "1. Set environment variables: NEON_HOST, NEON_DATABASE, NEON_USER, NEON_PASSWORD\n"
            "2. Create neon_config.json from template (development only)\n"
            "See .env.template or neon_config.template.json for reference."
        )


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
