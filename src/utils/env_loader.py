"""
Environment variable loader utility
Loads environment variables from .env file if it exists
"""

import os
from pathlib import Path


def load_env_file(env_path: str = ".env") -> bool:
    """
    Load environment variables from .env file

    Args:
        env_path: Path to the .env file

    Returns:
        True if file was loaded successfully, False otherwise
    """
    env_file = Path(env_path)

    if not env_file.exists():
        return False

    try:
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue

                # Parse key=value pairs
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()

                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]

                    # Only set if not already in environment
                    if key not in os.environ:
                        os.environ[key] = value

        return True

    except Exception as e:
        print(f"Warning: Could not load .env file: {e}")
        return False


def ensure_env_loaded():
    """
    Ensure environment variables are loaded from .env file
    This should be called at the start of the application
    """
    load_env_file()


# Auto-load .env file when this module is imported
ensure_env_loaded()
