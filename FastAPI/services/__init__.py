"""
Services package for Banking Support AI Agent Chatbot API.

This package contains all service classes for handling business logic:
- Chat Service: Conversation management and message history
- RAG Service: Knowledge base search and document management
- Feedback Service: User feedback collection and analysis
- Agent Service: Multi-agent routing and response generation

All services are initialized and exported here for convenience.

Modules:
    chat_service: ChatService for conversation management
    rag_service: RAGService for knowledge base operations
    feedback_service: FeedbackService for feedback handling
    agent_service: AgentService for multi-agent routing

Example:
    >>> from services import ChatService, RAGService, AgentService
    >>> chat_svc = ChatService()
    >>> await chat_svc.initialize()
    >>> history = await chat_svc.get_conversation_history("conv_123")
"""

from .chat_service import ChatService
from .rag_service import RAGService
from .feedback_service import FeedbackService
from .agent_service import AgentService

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
    
    Example:
        >>> chat_svc, rag_svc, fb_svc, agent_svc = create_services()
    """
    return (
        ChatService(),
        RAGService(),
        FeedbackService(),
        AgentService(),
    )
