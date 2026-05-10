"""
Configuration module for Banking Support AI Agent Chatbot
Contains all configuration settings, theme colors, and page configurations.
"""

# Page configuration
PAGE_CONFIG = {
    "page_title": "Banking Support AI Agent Chatbot",
    "page_icon": "🤖",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}

# Theme colors
THEME_COLORS = {
    "primary": "#1f77b4",
    "secondary": "#ff7f0e",
    "success": "#2ca02c",
    "error": "#d62728",
    "warning": "#ff9896",
    "info": "#17becf",
    "light_bg": "#f0f2f6",
    "dark_bg": "#111111",
    "text_primary": "#262730",
    "text_secondary": "#808080",
}

# Chat configuration
CHAT_CONFIG = {
    "max_messages": 100,
    "message_timeout": 3600,  # seconds
    "enable_message_rating": True,
    "enable_message_export": True,
}

# API configuration
API_CONFIG = {
    "timeout": 30,
    "max_retries": 3,
    "retry_delay": 1,  # seconds
}

# Model configuration
MODEL_CONFIG = {
    "model_name": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 2048,
    "top_p": 0.9,
}

# RAG configuration
RAG_CONFIG = {
    "chunk_size": 512,
    "overlap": 50,
    "top_k": 5,
    "similarity_threshold": 0.7,
}
