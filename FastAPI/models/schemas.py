"""
Request and Response schemas for Banking Support AI Agent Chatbot API.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============================================================================
# CHAT MODELS
# ============================================================================


class ChatRequest(BaseModel):
    """Chat message request."""
    conversation_id: str = Field(..., description="Unique conversation identifier")
    message: str = Field(..., description="User message")
    temperature: float = Field(default=0.7, ge=0.0, le=1.0, description="Response temperature")
    max_tokens: int = Field(default=2048, ge=100, le=4096, description="Max tokens in response")
    model: Optional[str] = Field(default="gpt-4", description="AI model to use")


class ChatResponse(BaseModel):
    """Chat message response."""
    conversation_id: str
    response: str
    agent_type: Optional[str] = None
    confidence: Optional[float] = None
    sources: Optional[List[Dict[str, Any]]] = None
    timestamp: str


class ConversationRequest(BaseModel):
    """Request for conversation operations."""
    conversation_id: str


class ConversationMessage(BaseModel):
    """A single message in conversation history."""
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


# ============================================================================
# KNOWLEDGE BASE / RAG MODELS
# ============================================================================


class RAGDocument(BaseModel):
    """RAG document result."""
    document_id: str
    title: str
    content: str
    category: Optional[str] = None
    relevance_score: float
    metadata: Optional[Dict[str, Any]] = None


class KnowledgeBaseSearchRequest(BaseModel):
    """Knowledge base search request."""
    query: str = Field(..., description="Search query")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of results")
    filters: Optional[Dict[str, Any]] = None


class KnowledgeBaseSearchResponse(BaseModel):
    """Knowledge base search response."""
    query: str
    results: List[RAGDocument]
    total_results: int
    timestamp: str


class DocumentToAdd(BaseModel):
    """Document to add to knowledge base."""
    title: str
    content: str
    category: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


# ============================================================================
# FEEDBACK MODELS
# ============================================================================


class FeedbackRequest(BaseModel):
    """User feedback request."""
    conversation_id: str
    message_id: str
    rating: int = Field(..., ge=1, le=5, description="Rating 1-5")
    feedback_text: Optional[str] = None
    email: Optional[str] = None


class FeedbackResponse(BaseModel):
    """Feedback submission response."""
    feedback_id: str
    status: str
    message: str


# ============================================================================
# AGENT MODELS
# ============================================================================


class AgentInfo(BaseModel):
    """Information about an agent."""
    agent_type: str
    name: str
    description: str
    capabilities: List[str]
    is_available: bool


class AgentResponse(BaseModel):
    """Response from an agent."""
    agent_type: str
    content: str
    confidence: float
    actions_taken: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


# ============================================================================
# SYSTEM MODELS
# ============================================================================


class ServiceStatus(BaseModel):
    """Status of a service."""
    service_name: str
    status: str  # "operational", "degraded", "down"
    last_check: Optional[str] = None


class SystemMetrics(BaseModel):
    """System metrics."""
    active_conversations: int
    total_messages_processed: int
    knowledge_base_documents: int
    average_response_time: float
    error_rate: float


class SystemStatus(BaseModel):
    """Overall system status."""
    timestamp: str
    services: Dict[str, str]
    metrics: Dict[str, Any]
