"""
Helper utilities for the MCP HF Hackathon application
"""

import re
from typing import List, Dict, Any, Optional


def process_user_input(text: str) -> str:
    """
    Process and clean user input

    Args:
        text: Raw user input text

    Returns:
        Cleaned and processed text
    """
    if not text:
        return ""

    # Basic cleaning
    text = text.strip()

    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text)

    return text


def validate_model_name(model_name: str, available_models: List[str]) -> bool:
    """
    Validate if a model name is available

    Args:
        model_name: Name of the model to validate
        available_models: List of available model names

    Returns:
        True if model is available, False otherwise
    """
    return model_name in available_models


def format_response(content: str, metadata: Dict[str, Any] = None) -> str:
    """
    Format response content with optional metadata

    Args:
        content: Main response content
        metadata: Optional metadata to include

    Returns:
        Formatted response string
    """
    if not metadata:
        return content

    formatted = f"{content}\n\n"

    if "model" in metadata:
        formatted += f"**Model:** {metadata['model']}\n"

    if "tokens_used" in metadata:
        formatted += f"**Tokens Used:** {metadata['tokens_used']}\n"

    return formatted


def parse_model_parameters(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse and validate model parameters

    Args:
        params: Raw parameter dictionary

    Returns:
        Validated parameter dictionary
    """
    validated = {}

    # Temperature validation
    if "temperature" in params:
        temp = float(params["temperature"])
        validated["temperature"] = max(0.0, min(2.0, temp))

    # Max tokens validation
    if "max_tokens" in params:
        max_tok = int(params["max_tokens"])
        validated["max_tokens"] = max(1, min(4000, max_tok))

    # Top-p validation
    if "top_p" in params:
        top_p = float(params["top_p"])
        validated["top_p"] = max(0.0, min(1.0, top_p))

    return validated


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to specified length

    Args:
        text: Text to truncate
        max_length: Maximum length

    Returns:
        Truncated text with ellipsis if needed
    """
    if len(text) <= max_length:
        return text

    return text[: max_length - 3] + "..."


def extract_keywords(text: str) -> List[str]:
    """
    Extract keywords from text

    Args:
        text: Input text

    Returns:
        List of extracted keywords
    """
    # Simple keyword extraction (can be enhanced with NLP libraries)
    words = re.findall(r"\b\w{3,}\b", text.lower())

    # Remove common stop words
    stop_words = {
        "the",
        "and",
        "but",
        "for",
        "with",
        "this",
        "that",
        "they",
        "them",
        "are",
        "was",
        "were",
        "been",
        "have",
        "has",
        "had",
        "will",
        "would",
        "could",
        "should",
        "can",
        "may",
        "might",
        "must",
        "shall",
    }

    keywords = [word for word in words if word not in stop_words]

    # Return unique keywords
    return list(set(keywords))
