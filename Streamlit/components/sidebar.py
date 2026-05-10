"""
Sidebar component for Banking Support AI Agent Chatbot
Renders the sidebar with navigation, settings, and conversation controls.
"""

import streamlit as st
from utils.session_manager import (
    clear_chat_history,
    reset_session,
    get_conversation_id,
    set_session_data,
)
from utils.logger import setup_logger
from config import THEME_COLORS

logger = setup_logger(__name__)


def render_sidebar() -> None:
    """
    Render the main sidebar with navigation and controls.
    """
    st.markdown(
        f"<h3 style='color: {THEME_COLORS['primary']};'>Navigation</h3>",
        unsafe_allow_html=True,
    )
    
    # Navigation menu
    menu_options = [
        "💬 Chat",
        "📚 Knowledge Base",
        "⚙️ Settings",
        "❓ FAQ",
        "📧 Feedback",
    ]
    
    selected_menu = st.radio("Select Option", menu_options, label_visibility="collapsed")
    
    st.markdown("---")
    
    # Conversation controls
    render_conversation_controls()
    
    st.markdown("---")
    
    # Settings section
    render_settings_section()
    
    st.markdown("---")
    
    # About section
    render_about_section()


def render_conversation_controls() -> None:
    """Render conversation control buttons."""
    st.markdown(
        f"<h4 style='color: {THEME_COLORS['secondary']};'>Conversation</h4>",
        unsafe_allow_html=True,
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            clear_chat_history()
            st.success("Chat history cleared!")
            logger.info("Chat history cleared by user")
            st.rerun()
    
    with col2:
        if st.button("🔄 New Chat", use_container_width=True):
            reset_session()
            st.success("New conversation started!")
            logger.info("New conversation started")
            st.rerun()
    
    # Display conversation ID
    st.markdown(
        f"""
        <div style='background-color: {THEME_COLORS['light_bg']}; 
                    padding: 0.75rem; border-radius: 0.25rem; margin-top: 1rem;'>
            <p style='font-size: 0.8rem; color: gray; margin: 0;'>
                <strong>Conversation ID:</strong><br/>
                <code>{get_conversation_id()[:8]}...</code>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_settings_section() -> None:
    """Render settings section."""
    st.markdown(
        f"<h4 style='color: {THEME_COLORS['secondary']};'>Settings</h4>",
        unsafe_allow_html=True,
    )
    
    # Theme toggle
    theme_mode = st.radio(
        "Theme",
        options=["Light", "Dark"],
        horizontal=True,
        label_visibility="collapsed",
    )
    set_session_data("theme_mode", theme_mode.lower())
    
    # Temperature slider
    temperature = st.slider(
        "Response Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Lower values make responses more focused, higher values more creative",
    )
    set_session_data("temperature", temperature)
    
    # Model selection
    model = st.selectbox(
        "Model",
        options=["GPT-4", "GPT-3.5", "Claude", "Llama"],
        help="Select the AI model to use for responses",
    )
    set_session_data("model", model)


def render_about_section() -> None:
    """Render about section with app information."""
    st.markdown(
        f"<h4 style='color: {THEME_COLORS['secondary']};'>About</h4>",
        unsafe_allow_html=True,
    )
    
    st.markdown(
        """
        **Banking Support AI Agent Chatbot v1.0**
        
        An intelligent multi-agent support system powered by advanced language models
        and retrieval-augmented generation (RAG).
        
        **Features:**
        - Multi-agent support resolution
        - Knowledge base search
        - Real-time responses
        - Conversation history
        - User feedback integration
        """
    )
    
    st.markdown("---")
    
    # Contact and links
    st.markdown("**Resources:**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("[📖 Documentation](#)")
    
    with col2:
        st.markdown("[💬 Support](#)")
    
    with col3:
        st.markdown("[🐛 Report Issue](#)")
