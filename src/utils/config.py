"""
Configuration utilities
"""

import json
import os
from typing import Dict, Any


def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    Load application configuration

    Args:
        config_path: Path to config file (optional)

    Returns:
        Configuration dictionary
    """
    if config_path is None:
        config_path = os.path.join("config", "app_config.json")

    # Default configuration
    default_config = {
        "server_name": "127.0.0.1",
        "server_port": 7860,
        "share": False,
        "debug": True,
        "default_model": "gpt-3.5-turbo",
        "max_tokens": 1000,
        "temperature": 0.7,
        "app_title": "MCP HF Hackathon",
        "app_description": "Model Context Protocol Integration with Hugging Face",
    }

    # Try to load from file
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                file_config = json.load(f)
                default_config.update(file_config)
        except Exception as e:
            print(f"Warning: Could not load config file {config_path}: {e}")

    # Override with environment variables
    env_overrides = {
        "server_port": os.getenv("PORT", default_config["server_port"]),
        "debug": os.getenv("DEBUG", "").lower() in ["true", "1", "yes"],
        "share": os.getenv("SHARE", "").lower() in ["true", "1", "yes"],
    }

    for key, value in env_overrides.items():
        if value is not None:
            default_config[key] = value

    return default_config


def save_config(config: Dict[str, Any], config_path: str = None):
    """
    Save configuration to file

    Args:
        config: Configuration dictionary to save
        config_path: Path to save config file
    """
    if config_path is None:
        config_path = os.path.join("config", "app_config.json")

    os.makedirs(os.path.dirname(config_path), exist_ok=True)

    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
