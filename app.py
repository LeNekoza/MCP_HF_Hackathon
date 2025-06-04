"""
MCP Hugging Face Hackathon - Main Application
A Gradio-based application for the Model Context Protocol Hugging Face Hackathon
"""

import gradio as gr
from src.components.interface import create_main_interface
from src.utils.config import load_config
from src.utils.logger import setup_logger

def main():
    """Main entry point for the application"""
    # Setup logging
    logger = setup_logger()
    logger.info("Starting MCP HF Hackathon application")
    
    # Load configuration
    config = load_config()
    
    # Create the main Gradio interface
    demo = create_main_interface(config)
    
    # Launch the application
    demo.launch(
        server_name=config.get("server_name", "127.0.0.1"),
        server_port=config.get("server_port", 7860),
        share=config.get("share", False),
        debug=config.get("debug", True),
        mcp_server=True
    )

if __name__ == "__main__":
    main()
