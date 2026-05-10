"""
FastAPI Backend for Banking Support AI Agent Chatbot

Provides APIs for:
- Chat message processing and conversation management
- RAG (Retrieval-Augmented Generation) knowledge base search
- Multi-agent routing and response generation
- User feedback collection and analysis
- System monitoring and health checks

Modules Used:
    - models: Request/response Pydantic schemas
    - services: Business logic services for chat, RAG, feedback, agents
    - config: Application configuration

API Routes:
    - /health: Health check
    - /chat: Send message and get response
    - /knowledge-base/*: Knowledge base operations
    - /feedback: Submit and retrieve feedback
    - /agents: List and manage agents
    - /system/status: System monitoring

Example:
    Run with: python main.py
    API available at: http://localhost:8000
    API docs: http://localhost:8000/docs
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from datetime import datetime

# Import models from models package
from models import (
    ChatRequest,
    ChatResponse,
    KnowledgeBaseSearchRequest,
    KnowledgeBaseSearchResponse,
    FeedbackRequest,
    FeedbackResponse,
    ConversationRequest,
)

# Import services from services package
from services import (
    ChatService,
    RAGService,
    FeedbackService,
    AgentService,
)

# Import configuration
from config import API_CONFIG, LOGGING_CONFIG

# Configure logging
logging.basicConfig(**LOGGING_CONFIG)
logger = logging.getLogger(__name__)

# Initialize services
chat_service = ChatService()
rag_service = RAGService()
feedback_service = FeedbackService()
agent_service = AgentService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    
    Manages application lifecycle:
    - Startup: Initialize all services
    - Shutdown: Cleanup resources
    """
    logger.info("Banking Support AI Agent Chatbot API Starting...")
    # Startup
    await chat_service.initialize()
    await rag_service.initialize()
    yield
    # Shutdown
    logger.info("Banking Support AI Agent Chatbot API Shutting down...")
    await chat_service.cleanup()


# Create FastAPI application
app = FastAPI(
    title="Banking Support AI Agent Chatbot API",
    description="API for Banking Support AI Agent Chatbot with RAG and Multi-Agent support",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Banking Support AI Agent Chatbot API",
        "version": "1.0.0",
    }


# ============================================================================
# CHAT ENDPOINTS
# ============================================================================


@app.post("/chat", response_model=ChatResponse)
async def process_chat(request: ChatRequest) -> ChatResponse:
    """
    Process a chat message and generate a response.
    
    - **conversation_id**: Unique conversation identifier
    - **message**: User's message
    - **temperature**: Response creativity (0.0-1.0)
    - **max_tokens**: Maximum tokens in response
    """
    try:
        logger.info(f"Processing chat message for conversation: {request.conversation_id}")
        
        # Get or create conversation
        conversation = await chat_service.get_or_create_conversation(
            request.conversation_id
        )
        
        # Add user message to history
        await chat_service.add_message(
            conversation_id=request.conversation_id,
            role="user",
            content=request.message,
        )
        
        # Search knowledge base
        rag_results = await rag_service.search_knowledge_base(
            query=request.message,
            top_k=API_CONFIG.get("rag_top_k", 5),
        )
        
        # Route to appropriate agent based on query
        agent_response = await agent_service.route_to_agent(
            message=request.message,
            rag_results=rag_results,
            conversation_id=request.conversation_id,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
        
        # Add assistant response to history
        await chat_service.add_message(
            conversation_id=request.conversation_id,
            role="assistant",
            content=agent_response["content"],
            metadata={
                "agent": agent_response.get("agent_type"),
                "confidence": agent_response.get("confidence"),
                "rag_used": len(rag_results) > 0,
            },
        )
        
        logger.info(f"Chat processed successfully for conversation: {request.conversation_id}")
        
        return ChatResponse(
            conversation_id=request.conversation_id,
            response=agent_response["content"],
            agent_type=agent_response.get("agent_type"),
            confidence=agent_response.get("confidence"),
            sources=rag_results,
            timestamp=datetime.now().isoformat(),
        )
    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/history")
async def get_conversation_history(request: ConversationRequest):
    """
    Retrieve conversation history.
    
    - **conversation_id**: Unique conversation identifier
    """
    try:
        history = await chat_service.get_conversation_history(
            request.conversation_id
        )
        return {
            "conversation_id": request.conversation_id,
            "messages": history,
            "total_messages": len(history),
        }
    except Exception as e:
        logger.error(f"Error retrieving history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/chat/conversation/{conversation_id}")
async def clear_conversation(conversation_id: str):
    """Clear a conversation history."""
    try:
        await chat_service.clear_conversation(conversation_id)
        return {"status": "success", "message": "Conversation cleared"}
    except Exception as e:
        logger.error(f"Error clearing conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# KNOWLEDGE BASE / RAG ENDPOINTS
# ============================================================================


@app.post("/knowledge-base/search", response_model=KnowledgeBaseSearchResponse)
async def search_knowledge_base(request: KnowledgeBaseSearchRequest):
    """
    Search the knowledge base using RAG.
    
    - **query**: Search query
    - **top_k**: Number of results to return (default: 5)
    """
    try:
        logger.info(f"Searching knowledge base with query: {request.query}")
        
        results = await rag_service.search_knowledge_base(
            query=request.query,
            top_k=request.top_k,
        )
        
        return KnowledgeBaseSearchResponse(
            query=request.query,
            results=results,
            total_results=len(results),
            timestamp=datetime.now().isoformat(),
        )
    except Exception as e:
        logger.error(f"Error searching knowledge base: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/knowledge-base/add-document")
async def add_document_to_knowledge_base(request: dict):
    """
    Add a document to the knowledge base.
    
    - **title**: Document title
    - **content**: Document content
    - **category**: Document category
    """
    try:
        logger.info(f"Adding document to knowledge base: {request.get('title')}")
        
        document_id = await rag_service.add_document(
            title=request.get("title"),
            content=request.get("content"),
            category=request.get("category"),
        )
        
        return {
            "status": "success",
            "document_id": document_id,
            "message": "Document added successfully",
        }
    except Exception as e:
        logger.error(f"Error adding document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/knowledge-base/stats")
async def get_knowledge_base_stats():
    """Get knowledge base statistics."""
    try:
        stats = await rag_service.get_knowledge_base_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting KB stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# FEEDBACK ENDPOINTS
# ============================================================================


@app.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackRequest):
    """
    Submit feedback for a chat response.
    
    - **conversation_id**: Conversation ID
    - **message_id**: Message ID
    - **rating**: Rating (1-5)
    - **feedback_text**: Feedback text
    """
    try:
        logger.info(f"Submitting feedback for message: {request.message_id}")
        
        feedback_id = await feedback_service.save_feedback(
            conversation_id=request.conversation_id,
            message_id=request.message_id,
            rating=request.rating,
            feedback_text=request.feedback_text,
            timestamp=datetime.now().isoformat(),
        )
        
        return FeedbackResponse(
            feedback_id=feedback_id,
            status="success",
            message="Feedback submitted successfully",
        )
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/feedback/statistics")
async def get_feedback_statistics():
    """Get feedback statistics."""
    try:
        stats = await feedback_service.get_feedback_statistics()
        return stats
    except Exception as e:
        logger.error(f"Error getting feedback stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# AGENT ENDPOINTS
# ============================================================================


@app.get("/agents")
async def list_agents():
    """List all available agents."""
    try:
        agents = await agent_service.list_available_agents()
        return {
            "agents": agents,
            "total_agents": len(agents),
        }
    except Exception as e:
        logger.error(f"Error listing agents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agents/{agent_type}")
async def get_agent_info(agent_type: str):
    """Get information about a specific agent."""
    try:
        agent_info = await agent_service.get_agent_info(agent_type)
        if not agent_info:
            raise HTTPException(status_code=404, detail=f"Agent {agent_type} not found")
        return agent_info
    except Exception as e:
        logger.error(f"Error getting agent info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SYSTEM ENDPOINTS
# ============================================================================


@app.get("/system/status")
async def get_system_status():
    """Get system status and metrics."""
    try:
        status = {
            "timestamp": datetime.now().isoformat(),
            "services": {
                "chat_service": "operational",
                "rag_service": "operational",
                "feedback_service": "operational",
                "agent_service": "operational",
            },
            "metrics": {
                "active_conversations": await chat_service.get_active_conversation_count(),
                "total_messages_processed": await chat_service.get_total_messages_processed(),
                "knowledge_base_documents": await rag_service.get_document_count(),
            },
        }
        return status
    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host=API_CONFIG.get("host", "0.0.0.0"),
        port=API_CONFIG.get("port", 8000),
    )
