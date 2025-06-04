"""
Logging utilities
"""

import logging
import os
from datetime import datetime

def setup_logger(name: str = None, level: str = "INFO") -> logging.Logger:
    """
    Setup application logger
    
    Args:
        name: Logger name (optional)
        level: Logging level
        
    Returns:
        Configured logger instance
    """
    if name is None:
        name = "mcp_hf_hackathon"
    
    logger = logging.getLogger(name)
    
    # Don't add handlers if they already exist
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, level.upper()))
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    simple_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # File handler (if logs directory exists)
    logs_dir = "logs"
    if os.path.exists(logs_dir) or os.makedirs(logs_dir, exist_ok=True):
        log_filename = f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
        log_filepath = os.path.join(logs_dir, log_filename)
        
        file_handler = logging.FileHandler(log_filepath)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    
    return logger
