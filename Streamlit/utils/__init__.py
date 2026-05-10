"""
Utils package for Banking Support AI Agent Chatbot.

This package contains utility modules for:
- Logging and debugging
- Session state management
- API client and communication
- Helper functions and utilities

Modules:
    logger: Logging configuration and setup
    session_manager: Streamlit session state management
    api_client: API communication client
    api_config: API configuration and endpoints

Example:
    >>> from utils import setup_logger, initialize_session_state, get_api_client
    >>> logger = setup_logger(__name__)
    >>> initialize_session_state()
    >>> api = get_api_client()
    >>> response = api.send_message("conv_123", "Hello")

Utility Functions:
    - setup_logger(name, level): Configure logger instance
    - get_logger(name): Retrieve configured logger
    - initialize_session_state(): Initialize session variables
    - add_message(role, content, metadata): Add to chat history
    - get_chat_history(): Retrieve chat messages
    - clear_chat_history(): Clear all messages
    - get_conversation_id(): Get current conversation ID
    - get_api_client(base_url): Get or create API client
"""

from .logger import setup_logger, get_logger
from .session_manager import (
    initialize_session_state,
    add_message,
    get_chat_history,
    clear_chat_history,
    get_session_data,
    set_session_data,
    get_conversation_id,
    reset_session,
)
from .api_client import ChatbotAPIClient, get_api_client

__all__ = [
    # Logger utilities
    "setup_logger",
    "get_logger",
    # Session manager utilities
    "initialize_session_state",
    "add_message",
    "get_chat_history",
    "clear_chat_history",
    "get_session_data",
    "set_session_data",
    "get_conversation_id",
    "reset_session",
    # API client utilities
    "ChatbotAPIClient",
    "get_api_client",
]

__version__ = "1.0.0"
__author__ = "Banking Support Team"
__description__ = "Utility modules for Banking Support AI Agent Chatbot"
