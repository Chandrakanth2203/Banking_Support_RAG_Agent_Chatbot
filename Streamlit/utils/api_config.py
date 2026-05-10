"""
API Configuration for Streamlit App.
"""

import os

# API Base URL
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# API Endpoints
CHAT_ENDPOINT = "/chat"
HISTORY_ENDPOINT = "/chat/history"
SEARCH_KB_ENDPOINT = "/knowledge-base/search"
FEEDBACK_ENDPOINT = "/feedback"
AGENTS_ENDPOINT = "/agents"
HEALTH_ENDPOINT = "/health"

# Request timeouts
REQUEST_TIMEOUT = 30
HEALTH_CHECK_TIMEOUT = 5

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds
