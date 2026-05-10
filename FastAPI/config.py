"""
Configuration for Banking Support AI Agent Chatbot API.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
API_CONFIG = {
    "host": os.getenv("API_HOST", "0.0.0.0"),
    "port": int(os.getenv("API_PORT", 8000)),
    "debug": os.getenv("API_DEBUG", "False") == "True",
    "timeout": 30,
    "max_retries": 3,
    "retry_delay": 1,
    "rag_top_k": 5,
}

# Model Configuration
MODEL_CONFIG = {
    "model_name": os.getenv("MODEL_NAME", "gpt-4"),
    "temperature": float(os.getenv("TEMPERATURE", 0.7)),
    "max_tokens": int(os.getenv("MAX_TOKENS", 2048)),
    "top_p": float(os.getenv("TOP_P", 0.9)),
}

# RAG Configuration
RAG_CONFIG = {
    "chunk_size": 512,
    "overlap": 50,
    "top_k": 5,
    "similarity_threshold": 0.7,
}

# Chat Configuration
CHAT_CONFIG = {
    "max_messages": 100,
    "message_timeout": 3600,
    "enable_message_rating": True,
    "enable_message_export": True,
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "datefmt": "%Y-%m-%d %H:%M:%S",
}

# Database Configuration (for future use)
DATABASE_CONFIG = {
    "db_type": os.getenv("DB_TYPE", "sqlite"),
    "db_path": os.getenv("DB_PATH", "chatbot.db"),
}

# CORS Configuration
CORS_CONFIG = {
    "allow_origins": ["*"],
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}

# Security Configuration
SECURITY_CONFIG = {
    "api_key_header": "X-API-Key",
    "require_auth": os.getenv("REQUIRE_AUTH", "False") == "True",
}
