"""
MCP Hugging Face Hackathon - Main Application
A Gradio-based application for the Model Context Protocol Hugging Face Hackathon
"""

import io
import os
import sys

import gradio as gr

from src.components.interface import create_main_interface
from src.utils.config import load_config
from src.utils.logger import setup_logger

# Ensure stdout/stderr support UTF-8 on Windows for emoji output
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def main():
    """Main entry point for the application"""
    # Setup logging
    logger = setup_logger()
    logger.info("Starting MCP HF Hackathon application")

    # Load configuration
    config = load_config()

    # Create the main Gradio interface
    demo = create_main_interface(config)  # Configure launch parameters
    launch_params = {
        "debug": os.getenv("GRADIO_DEBUG", "false").lower() == "true",
        "show_error": True,
        "inbrowser": not bool(os.getenv("NO_BROWSER", False)),
        "server_name": config.get("server_name", "0.0.0.0"),
        "server_port": config.get("server_port", 7860),
        "share": config.get("share", False),
        "show_api": False,
        "quiet": False,
    }

    # MCP server disabled due to Windows encoding issues
    # if hasattr(demo, 'launch') and 'mcp_server' in demo.launch.__code__.co_varnames:
    # launch_params["mcp_server"] = True

    # Launch the application
    logger.info(f"Launching application with params: {launch_params}")
    demo.launch(**launch_params)


if __name__ == "__main__":
    main()
