"""
Session Manager module for Support Resolution Chatbot
Manages session state and data persistence across Streamlit reruns.
"""

import streamlit as st
from typing import Any, Optional


def initialize_session_state() -> None:
    """
    Initialize all necessary session state variables.
    Called once at application startup.
    
    Session state variables include:
        - chat_history: List of chat messages
        - user_input: Current user input
        - conversation_id: Unique conversation identifier
        - session_data: Additional session metadata
    """
    # Initialize chat history if not present
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Initialize user input
    if "user_input" not in st.session_state:
        st.session_state.user_input = ""
    
    # Initialize conversation ID
    if "conversation_id" not in st.session_state:
        import uuid
        st.session_state.conversation_id = str(uuid.uuid4())
    
    # Initialize session metadata
    if "session_data" not in st.session_state:
        st.session_state.session_data = {
            "start_time": None,
            "message_count": 0,
            "active": True,
            "user_name": "User",
        }
    
    # Initialize UI state
    if "show_settings" not in st.session_state:
        st.session_state.show_settings = False
    
    if "theme_mode" not in st.session_state:
        st.session_state.theme_mode = "light"


def add_message(role: str, content: str, metadata: Optional[dict] = None) -> None:
    """
    Add a message to the chat history.
    
    Args:
        role (str): Role of the message sender ('user' or 'assistant')
        content (str): Content of the message
        metadata (Optional[dict]): Additional metadata for the message
    
    Example:
        >>> add_message("user", "What is your name?")
        >>> add_message("assistant", "I'm a support chatbot")
    """
    message = {
        "role": role,
        "content": content,
        "metadata": metadata or {}
    }
    st.session_state.chat_history.append(message)
    st.session_state.session_data["message_count"] += 1


def get_chat_history() -> list:
    """
    Get the current chat history.
    
    Returns:
        list: List of messages in the chat history
    """
    return st.session_state.get("chat_history", [])


def clear_chat_history() -> None:
    """Clear the entire chat history."""
    st.session_state.chat_history = []
    st.session_state.session_data["message_count"] = 0


def get_session_data(key: str, default: Any = None) -> Any:
    """
    Retrieve a value from session data.
    
    Args:
        key (str): Key to retrieve
        default (Any): Default value if key doesn't exist
    
    Returns:
        Any: Value from session data or default
    """
    return st.session_state.session_data.get(key, default)


def set_session_data(key: str, value: Any) -> None:
    """
    Set a value in session data.
    
    Args:
        key (str): Key to set
        value (Any): Value to set
    """
    st.session_state.session_data[key] = value


def get_conversation_id() -> str:
    """
    Get the current conversation ID.
    
    Returns:
        str: Conversation ID
    """
    return st.session_state.get("conversation_id", "")


def reset_session() -> None:
    """Reset the entire session to initial state."""
    st.session_state.clear()
    initialize_session_state()
