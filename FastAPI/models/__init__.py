"""
Models package for Banking Support AI Agent Chatbot API.

This package contains Pydantic models and schemas for request/response validation.
All models are imported here for convenient access throughout the application.

Modules:
    schemas: Pydantic request and response schemas

Example:
    >>> from models import ChatRequest, ChatResponse
    >>> request = ChatRequest(
    ...     conversation_id="conv_123",
    ...     message="Hello",
    ...     temperature=0.7
    ... )
"""

from .schemas import (
    # Chat Models
    ChatRequest,
    ChatResponse,
    ConversationRequest,
    ConversationMessage,
    # RAG Models
    RAGDocument,
    KnowledgeBaseSearchRequest,
    KnowledgeBaseSearchResponse,
    DocumentToAdd,
    # Feedback Models
    FeedbackRequest,
    FeedbackResponse,
    # Agent Models
    AgentInfo,
    AgentResponse,
    # System Models
    ServiceStatus,
    SystemMetrics,
    SystemStatus,
)

__all__ = [
    # Chat Models
    "ChatRequest",
    "ChatResponse",
    "ConversationRequest",
    "ConversationMessage",
    # RAG Models
    "RAGDocument",
    "KnowledgeBaseSearchRequest",
    "KnowledgeBaseSearchResponse",
    "DocumentToAdd",
    # Feedback Models
    "FeedbackRequest",
    "FeedbackResponse",
    # Agent Models
    "AgentInfo",
    "AgentResponse",
    # System Models
    "ServiceStatus",
    "SystemMetrics",
    "SystemStatus",
]

__version__ = "1.0.0"
__author__ = "Banking Support Team"
__description__ = "Models and schemas for Banking Support AI Agent Chatbot API"
