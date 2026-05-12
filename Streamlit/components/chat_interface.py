"""
Chat Interface component for Banking Support AI Agent Chatbot
Renders the main chat interface with message display and input handling.
"""

import streamlit as st
from datetime import datetime
from typing import Optional
from utils.session_manager import (
    add_message,
    get_chat_history,
    get_session_data,
    get_conversation_id,
)
from utils.logger import setup_logger
from utils.service_interface import get_service_interface
from config import THEME_COLORS, CHAT_CONFIG

logger = setup_logger(__name__)


def render_chat_interface() -> None:
    """
    Render the main chat interface with message history and input area.
    """
    # Create main container
    chat_container = st.container()
    
    with chat_container:
        # Display chat history
        render_chat_history()
        
        st.markdown("---")
        
        # Chat input area
        render_chat_input()


def render_chat_history() -> None:
    """Render the chat message history."""
    chat_history = get_chat_history()
    
    if not chat_history:
        # Empty state
        st.markdown(
            f"""
            <div style='text-align: center; padding: 3rem 1rem; color: gray;'>
                <h3>👋 Welcome to Banking Support AI Agent Chatbot</h3>
                <p>Start a conversation by typing a message below.</p>
                <p style='font-size: 0.9rem;'>
                    Ask me anything about our support services, products, or policies.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        # Display messages
        for idx, message in enumerate(chat_history):
            render_message(message, idx)


def render_message(
    message: dict,
    index: int,
) -> None:
    """
    Render a single chat message.
    
    Args:
        message (dict): Message dictionary with 'role', 'content', and optional 'metadata'
        index (int): Index of the message in the chat history
    """
    role = message.get("role", "assistant")
    content = message.get("content", "")
    metadata = message.get("metadata", {})
    
    # Determine message styling based on role
    if role == "user":
        render_user_message(content, metadata, index)
    elif role == "assistant":
        render_assistant_message(content, metadata, index)
    else:
        render_system_message(content, metadata)


def render_user_message(content: str, metadata: dict, index: int) -> None:
    """
    Render a user message.
    
    Args:
        content (str): Message content
        metadata (dict): Message metadata
        index (int): Message index
    """
    with st.chat_message("user", avatar="👤"):
        st.markdown(content)
        
        # Optional: Show metadata
        if metadata:
            render_message_metadata(metadata)


def render_assistant_message(content: str, metadata: dict, index: int) -> None:
    """
    Render an assistant message.
    
    Args:
        content (str): Message content
        metadata (dict): Message metadata
        index (int): Message index
    """
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown(content)
        
        # Optional: Show metadata and feedback buttons
        if metadata:
            render_message_metadata(metadata)
        
        # Message feedback
        if CHAT_CONFIG.get("enable_message_rating", True):
            render_message_feedback(index)


def render_system_message(content: str, metadata: dict) -> None:
    """
    Render a system message.
    
    Args:
        content (str): Message content
        metadata (dict): Message metadata
    """
    st.info(f"ℹ️ {content}")


def render_message_metadata(metadata: dict) -> None:
    """
    Render message metadata (timestamp, token count, etc.).
    
    Args:
        metadata (dict): Message metadata dictionary
    """
    cols = st.columns(3)
    
    if "timestamp" in metadata:
        with cols[0]:
            st.caption(f"⏱️ {metadata['timestamp']}")
    
    if "tokens" in metadata:
        with cols[1]:
            st.caption(f"📊 {metadata['tokens']} tokens")
    
    if "model" in metadata:
        with cols[2]:
            st.caption(f"🤖 {metadata['model']}")


def render_message_feedback(message_index: int) -> None:
    """
    Render message feedback controls (like/dislike buttons).
    
    Args:
        message_index (int): Index of the message
    """
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("👍 Helpful", key=f"helpful_{message_index}", use_container_width=True):
            logger.info(f"Message {message_index} marked as helpful")
            st.toast("Thanks for the feedback!")
    
    with col2:
        if st.button("👎 Not Helpful", key=f"not_helpful_{message_index}", use_container_width=True):
            logger.info(f"Message {message_index} marked as not helpful")
            st.toast("We'll improve this!")
    
    with col3:
        if st.button("📋 Copy", key=f"copy_{message_index}", use_container_width=True):
            st.toast("Copied to clipboard!")
    
    with col4:
        if st.button("📤 Share", key=f"share_{message_index}", use_container_width=True):
            st.toast("Share link copied!")


def render_chat_input() -> None:
    """Render the chat input area."""
    st.markdown(
        f"<h4 style='color: {THEME_COLORS['primary']};'>Your Message</h4>",
        unsafe_allow_html=True,
    )
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_input = st.text_input(
            "Type your message here...",
            placeholder="Ask a question or describe your issue...",
            label_visibility="collapsed",
            key="user_input",
        )
    
    with col2:
        send_button = st.button(
            "📤 Send",
            use_container_width=True,
            type="primary",
        )
    
    # Process user input
    if send_button and user_input.strip():
        handle_user_input(user_input)


def handle_user_input(user_input: str) -> None:
    """
    Handle user input and generate a response.
    
    Args:
        user_input (str): The user's input message
    """
    # Add user message to history
    add_message(
        role="user",
        content=user_input,
        metadata={"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
    )
    
    logger.info(f"User input received: {user_input[:100]}")
    
    # Show typing indicator
    with st.spinner("🤔 Processing your request..."):
        # Call service to get response
        service = get_service_interface()
        response_data = service.send_message(
            conversation_id=get_conversation_id(),
            message=user_input,
            temperature=get_session_data("temperature", 0.7),
            max_tokens=2048,
        )
        
        if response_data:
            response = response_data.get("response", "Error processing request")
            agent_type = response_data.get("agent_type", "unknown")
            confidence = response_data.get("confidence", 0)
        else:
            response = "I apologize, but I'm unable to process your request at the moment. Please try again later."
            agent_type = None
            confidence = None
        
        # Add assistant response to history
        add_message(
            role="assistant",
            content=response,
            metadata={
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "model": get_session_data("model", "GPT-4"),
                "agent": agent_type,
                "confidence": confidence,
            },
        )
    
    logger.info("Response generated and added to history")
    st.rerun()

