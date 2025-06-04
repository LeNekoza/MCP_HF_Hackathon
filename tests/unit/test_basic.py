"""
Basic test for the main application
"""

import pytest
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.config import load_config
from utils.helpers import process_user_input, validate_model_name
from models.mcp_handler import MCPHandler

def test_load_config():
    """Test configuration loading"""
    config = load_config()
    assert isinstance(config, dict)
    assert "server_port" in config
    assert "default_model" in config

def test_process_user_input():
    """Test user input processing"""
    # Test basic cleaning
    result = process_user_input("  Hello   world  ")
    assert result == "Hello world"
    
    # Test empty input
    result = process_user_input("")
    assert result == ""
    
    # Test None input
    result = process_user_input(None)
    assert result == ""

def test_validate_model_name():
    """Test model name validation"""
    available_models = ["gpt-3.5-turbo", "gpt-4", "claude-3-sonnet"]
    
    assert validate_model_name("gpt-3.5-turbo", available_models) == True
    assert validate_model_name("invalid-model", available_models) == False

def test_mcp_handler_initialization():
    """Test MCP handler initialization"""
    config = {"default_model": "gpt-3.5-turbo"}
    handler = MCPHandler(config)
    
    assert handler.config == config
    assert "available" in handler.models
    assert len(handler.models["available"]) > 0

def test_mcp_handler_process_request():
    """Test MCP handler request processing"""
    config = {"default_model": "gpt-3.5-turbo"}
    handler = MCPHandler(config)
    
    response = handler.process_request("Hello, world!")
    
    assert isinstance(response, dict)
    assert "content" in response
    assert "status" in response
    assert response["status"] == "success"
