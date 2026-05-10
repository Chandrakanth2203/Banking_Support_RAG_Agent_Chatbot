"""
Logger configuration module for Banking Support AI Agent Chatbot
Provides logging setup and configuration for the application.
"""

import logging
import sys
from datetime import datetime


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Setup and configure a logger with the given name.
    
    Args:
        name (str): Name of the logger (typically __name__)
        level (int): Logging level (default: logging.INFO)
    
    Returns:
        logging.Logger: Configured logger instance
    
    Example:
        >>> logger = setup_logger(__name__)
        >>> logger.info("Application started")
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid adding multiple handlers
    if logger.hasHandlers():
        return logger
    
    # Create formatters
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance by name.
    
    Args:
        name (str): Name of the logger
    
    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)
