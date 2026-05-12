"""
Services package for Banking Support AI Agent Chatbot API.

This package contains service classes for handling business logic:
- Chat Service: Conversation management and message history
- Feedback Service: User feedback collection and analysis
- Agent Service: Multi-agent routing and response generation

RAG Service is located in the RAG folder for separation of concerns.

All services are initialized and exported here for convenience.

Modules:
    chat_service: ChatService for conversation management
    feedback_service: FeedbackService for feedback handling
    agent_service: AgentService for multi-agent routing

Related:
    RAG package: Located at ../RAG/ for knowledge base operations

Example:
    >>> from services import ChatService, FeedbackService, AgentService
    >>> from RAG import RAGService
    >>> chat_svc = ChatService()
    >>> await chat_svc.initialize()
    >>> history = await chat_svc.get_conversation_history("conv_123")
"""

from .chat_service import ChatService
from .feedback_service import FeedbackService
from .agent_service import AgentService

# RAG Service is imported from FastAPI folder (not RAG folder)
# This keeps the service orchestration layer in FastAPI
import sys
from pathlib import Path

# Add paths for imports
_fastapi_path = Path(__file__).parent.parent
_root_path = _fastapi_path.parent

if str(_root_path) not in sys.path:
    sys.path.insert(0, str(_root_path))

try:
    from FastAPI.rag_service import RAGService
except ImportError as e:
    # Alternative import attempt
    try:
        sys.path.insert(0, str(_fastapi_path))
        from rag_service import RAGService
    except ImportError:
        raise ImportError(f"RAGService not found. Error: {str(e)}")

__all__ = [
    "ChatService",
    "RAGService",
    "FeedbackService",
    "AgentService",
]

__version__ = "1.0.0"
__author__ = "Banking Support Team"
__description__ = "Services for Banking Support AI Agent Chatbot API"


def create_services():
    """
    Create and return all service instances.
    
    Returns:
        tuple: (ChatService, RAGService, FeedbackService, AgentService)
    
    Note:
        RAGService is imported from RAG folder instead of local module
        to maintain separation of concerns between RAG and other services.
    
    Example:
        >>> chat_svc, rag_svc, fb_svc, agent_svc = create_services()
    """
    return (
        ChatService(),
        RAGService(),
        FeedbackService(),
        AgentService(),
    )
