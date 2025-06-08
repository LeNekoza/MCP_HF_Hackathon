"""
Configuration utilities
"""

import os
from typing import Dict, Any


def load_config() -> Dict[str, Any]:
    """
    Load application configuration from environment variables

    Returns:
        Configuration dictionary
    """
    # Load configuration from environment variables with defaults
    config = {
        "server_name": os.getenv("SERVER_NAME", "127.0.0.1"),
        "server_port": int(os.getenv("SERVER_PORT", "7860")),
        "share": os.getenv("SHARE", "false").lower() in ["true", "1", "yes"],
        "debug": os.getenv("DEBUG", "true").lower() in ["true", "1", "yes"],
        "default_model": os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo"),
        "max_tokens": int(os.getenv("MAX_TOKENS", "1000")),
        "temperature": float(os.getenv("TEMPERATURE", "0.7")),
        "app_title": os.getenv("APP_TITLE", "MCP HF Hackathon"),
        "app_description": os.getenv(
            "APP_DESCRIPTION", "Model Context Protocol Integration with Hugging Face"
        ),
        "models": {
            "available": os.getenv(
                "AVAILABLE_MODELS",
                "gpt-3.5-turbo,gpt-4,claude-3-sonnet,llama-2-7b,mistral-7b,nebius-llama-3.3-70b",
            ).split(","),
            "huggingface": {
                "api_url": os.getenv(
                    "HF_API_URL", "https://api-inference.huggingface.co/models/"
                ),
                "cache_dir": os.getenv("HF_CACHE_DIR", "./data/models"),
            },
            "nebius": {
                "model": os.getenv(
                    "NEBIUS_MODEL_NAME", "meta-llama/Llama-3.3-70B-Instruct"
                ),
                "api_url": os.getenv(
                    "NEBIUS_API_URL", "https://api.studio.nebius.ai/v1"
                ),
                "enabled": os.getenv("NEBIUS_ENABLED", "true").lower()
                in ["true", "1", "yes"],
            },
        },
        "mcp": {
            "enabled": os.getenv("MCP_ENABLED", "true").lower() in ["true", "1", "yes"],
            "version": os.getenv("MCP_VERSION", "1.0"),
            "protocol_features": os.getenv(
                "MCP_PROTOCOL_FEATURES",
                "context_management,model_switching,response_streaming",
            ).split(","),
        },
    }

    # Legacy environment variable overrides for backwards compatibility
    if os.getenv("PORT"):
        config["server_port"] = int(os.getenv("PORT"))

    return config


def get_env_bool(key: str, default: bool = False) -> bool:
    """
    Get boolean value from environment variable

    Args:
        key: Environment variable key
        default: Default value if not found

    Returns:
        Boolean value
    """
    value = os.getenv(key)
    if value is None:
        return default
    return value.lower() in ["true", "1", "yes", "on"]


def get_env_int(key: str, default: int = 0) -> int:
    """
    Get integer value from environment variable

    Args:
        key: Environment variable key
        default: Default value if not found

    Returns:
        Integer value
    """
    value = os.getenv(key)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def get_env_float(key: str, default: float = 0.0) -> float:
    """
    Get float value from environment variable

    Args:
        key: Environment variable key
        default: Default value if not found

    Returns:
        Float value
    """
    value = os.getenv(key)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default
