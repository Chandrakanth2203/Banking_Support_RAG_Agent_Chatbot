"""
Banking Support AI Agent Chatbot - Main Streamlit Application
This module serves as the entry point for the chatbot UI interface.
"""

import streamlit as st
from config import PAGE_CONFIG, THEME_COLORS
from components.chat_interface import render_chat_interface
from components.sidebar import render_sidebar
from components.header import render_header
from utils.session_manager import initialize_session_state
from utils.logger import setup_logger

# Setup logging
logger = setup_logger(__name__)

# Configure page settings
st.set_page_config(**PAGE_CONFIG)

# Apply custom styling
st.markdown(
    """
    <style>
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session state
initialize_session_state()

# Render header
render_header()

# Create layout with sidebar and main content
with st.sidebar:
    render_sidebar()

# Main chat interface
render_chat_interface()

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray; font-size: 0.8rem;'>"
    "Banking Support AI Agent Chatbot v1.0 | Powered by Streamlit</div>",
    unsafe_allow_html=True,
)
