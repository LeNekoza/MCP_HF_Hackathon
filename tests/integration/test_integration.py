"""
Integration tests for the MCP HF Hackathon application
"""

import pytest
import sys
import os
import requests
import time
from threading import Thread

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from utils.config import load_config

@pytest.fixture(scope="module")
def app_config():
    """Load application configuration for tests"""
    return load_config()

@pytest.fixture(scope="module") 
def test_server_url(app_config):
    """Get the test server URL"""
    host = app_config.get("server_name", "127.0.0.1")
    port = app_config.get("server_port", 7860)
    return f"http://{host}:{port}"

@pytest.mark.integration
def test_config_loading():
    """Test that configuration loads correctly"""
    config = load_config()
    
    # Check required configuration keys
    required_keys = ["server_name", "server_port", "default_model"]
    for key in required_keys:
        assert key in config, f"Required config key '{key}' is missing"
    
    # Check data types
    assert isinstance(config["server_port"], int)
    assert isinstance(config["debug"], bool)
    assert isinstance(config["default_model"], str)

@pytest.mark.integration
def test_model_configuration():
    """Test model configuration settings"""
    config = load_config()
    
    # Check MCP configuration
    assert "mcp" in config
    mcp_config = config["mcp"]
    
    assert "enabled" in mcp_config
    assert "version" in mcp_config
    assert "protocol_features" in mcp_config
    
    # Check models configuration
    assert "models" in config
    models_config = config["models"]
    
    assert "available" in models_config
    assert isinstance(models_config["available"], list)
    assert len(models_config["available"]) > 0

@pytest.mark.integration
@pytest.mark.slow
def test_application_startup():
    """Test that the application can start without errors"""
    # This is a basic test to ensure imports work
    try:
        from components.interface import create_main_interface
        from models.mcp_handler import MCPHandler
        from utils.logger import setup_logger
        
        # Test logger setup
        logger = setup_logger()
        assert logger is not None
        
        # Test MCP handler initialization
        config = load_config()
        handler = MCPHandler(config)
        assert handler is not None
        
        # Test interface creation (without launching)
        # Note: This doesn't actually launch the Gradio app
        interface = create_main_interface(config)
        assert interface is not None
        
    except ImportError as e:
        pytest.fail(f"Import error during startup test: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error during startup test: {e}")

# Note: The following test would require actually starting the server
# and is commented out as it's more complex to implement properly
"""
@pytest.mark.integration
@pytest.mark.slow
def test_server_response(test_server_url):
    \"\"\"Test that the server responds to requests\"\"\"
    # This test would require starting the actual Gradio server
    # which is complex in a test environment
    pass
"""
