"""
Components package for Banking Support AI Agent Chatbot.

This package contains all reusable Streamlit UI components for the chatbot interface.
Each component is self-contained and can be used independently.

Modules:
    header: Header component with title and status indicators
    sidebar: Sidebar with navigation, settings, and controls
    chat_interface: Main chat interface with message display and input

Example:
    >>> from components import render_header, render_sidebar, render_chat_interface
    >>> render_header()
    >>> with st.sidebar:
    ...     render_sidebar()
    >>> render_chat_interface()

Component Structure:
    - header.py
        - render_header(): Main header component
        - render_status_badge(): Status indicator component
    
    - sidebar.py
        - render_sidebar(): Main sidebar component
        - render_conversation_controls(): Conversation management
        - render_settings_section(): User settings
        - render_about_section(): About and resources
    
    - chat_interface.py
        - render_chat_interface(): Main chat component
        - render_chat_history(): Message history display
        - render_chat_input(): Message input area
        - render_message(): Individual message rendering
        - render_message_feedback(): Feedback buttons
"""

from .header import render_header
from .sidebar import render_sidebar
from .chat_interface import render_chat_interface

__all__ = [
    "render_header",
    "render_sidebar",
    "render_chat_interface",
]

__version__ = "1.0.0"
__author__ = "Banking Support Team"
__description__ = "Streamlit UI components for Banking Support AI Agent Chatbot"
