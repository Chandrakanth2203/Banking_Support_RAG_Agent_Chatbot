"""
Header component for Banking Support AI Agent Chatbot
Renders the application header with title and status indicators.
"""

import streamlit as st
from config import THEME_COLORS


def render_header() -> None:
    """
    Render the application header with title, description, and status.
    """
    # Main title
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.markdown(
            f"""
            <h1 style='color: {THEME_COLORS["primary"]}; margin-bottom: 0;'>
                🤖 Banking Support AI Agent Chatbot
            </h1>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p style='color: gray; margin-top: 0; font-size: 0.9rem;'>"
            "Intelligent multi-agent support resolution system"
            "</p>",
            unsafe_allow_html=True,
        )
    
    with col2:
        # Status indicator
        st.markdown(
            f"""
            <div style='text-align: right; padding-top: 0.5rem;'>
                <span style='color: green; font-weight: bold;'>● Online</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    # Divider
    st.markdown("---")


def render_status_badge(status: str, color: str = "green") -> None:
    """
    Render a status badge.
    
    Args:
        status (str): Status text to display
        color (str): Color of the badge (default: 'green')
    """
    st.markdown(
        f"""
        <span style='
            background-color: {color};
            color: white;
            padding: 0.25rem 0.5rem;
            border-radius: 0.25rem;
            font-size: 0.8rem;
            font-weight: bold;
        '>
            {status}
        </span>
        """,
        unsafe_allow_html=True,
    )


def render_info_section(title: str, content: str) -> None:
    """
    Render an information section in the header.
    
    Args:
        title (str): Section title
        content (str): Section content
    """
    st.markdown(
        f"""
        <div style='background-color: {THEME_COLORS["light_bg"]}; 
                    padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;'>
            <h4 style='margin-top: 0;'>{title}</h4>
            <p style='margin-bottom: 0; color: gray;'>{content}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
