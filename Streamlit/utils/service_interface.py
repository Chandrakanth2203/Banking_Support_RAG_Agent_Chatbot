"""
Service Interface for Banking Support AI Agent Chatbot - Streamlit.
Provides direct access to FastAPI services without HTTP layer.
Handles async-to-sync conversion for Streamlit compatibility.
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

# Add root and subdirectory paths to import FastAPI and RAG modules
root_path = Path(__file__).parent.parent.parent
fastapi_path = root_path / "FastAPI"
rag_path = root_path / "RAG"

# Add root directory first so RAG and FastAPI can be imported
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

# Then add FastAPI folder so services can be imported
if str(fastapi_path) not in sys.path:
    sys.path.insert(0, str(fastapi_path))

# Import services from FastAPI
try:
    from services import ChatService, FeedbackService, AgentService
    from RAG import RAGService
except ImportError as e:
    logger.error(f"Failed to import services: {str(e)}")
    raise


class ServiceInterface:
    """
    Unified interface for accessing FastAPI services from Streamlit.
    Handles async service calls in a synchronous Streamlit context.
    """
    
    def __init__(self):
        """Initialize all services."""
        self.chat_service = ChatService()
        self.feedback_service = FeedbackService()
        self.agent_service = AgentService()
        self.rag_service = RAGService()
        self.logger = logger
        
    def _run_async(self, coro):
        """
        Run async coroutine in Streamlit's synchronous context.
        
        Args:
            coro: Async coroutine to execute
            
        Returns:
            Result of the coroutine
        """
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(coro)
    
    async def initialize(self):
        """Initialize services."""
        await self.chat_service.initialize()
        await self.rag_service.initialize()
        self.logger.info("All services initialized")
    
    # ========================================================================
    # CHAT OPERATIONS
    # ========================================================================
    
    def send_message(
        self,
        conversation_id: str,
        message: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> Optional[Dict[str, Any]]:
        """
        Send a message and generate a response.
        Orchestrates chat service, RAG retrieval, and agent routing.
        
        Args:
            conversation_id: Unique conversation identifier
            message: User message
            temperature: Model temperature (0.0-1.0)
            max_tokens: Maximum tokens in response
            
        Returns:
            Response dict with response text, agent type, confidence, and sources
        """
        try:
            self.logger.info(f"Processing message for conversation: {conversation_id}")
            
            # Run async operations
            result = self._run_async(
                self._send_message_async(
                    conversation_id, message, temperature, max_tokens
                )
            )
            
            return result
        except Exception as e:
            self.logger.error(f"Error sending message: {str(e)}")
            return None
    
    async def _send_message_async(
        self,
        conversation_id: str,
        message: str,
        temperature: float,
        max_tokens: int,
    ) -> Dict[str, Any]:
        """Async implementation of send_message."""
        # Get or create conversation
        conversation = await self.chat_service.get_or_create_conversation(conversation_id)
        
        # Add user message
        await self.chat_service.add_message(
            conversation_id=conversation_id,
            role="user",
            content=message,
        )
        
        # Search RAG knowledge base
        rag_results = await self.rag_service.search_knowledge_base(
            query=message,
            top_k=5,
        )
        
        # Route to appropriate agent
        agent_response = await self.agent_service.route_to_agent(
            message=message,
            rag_results=rag_results,
            conversation_id=conversation_id,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        # Add assistant response
        await self.chat_service.add_message(
            conversation_id=conversation_id,
            role="assistant",
            content=agent_response.get("content", ""),
            metadata={
                "agent": agent_response.get("agent_type"),
                "confidence": agent_response.get("confidence"),
                "rag_used": len(rag_results) > 0,
            },
        )
        
        return {
            "conversation_id": conversation_id,
            "response": agent_response.get("content", ""),
            "agent_type": agent_response.get("agent_type"),
            "confidence": agent_response.get("confidence"),
            "sources": rag_results,
        }
    
    def get_conversation_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get conversation history."""
        try:
            result = self._run_async(
                self.chat_service.get_conversation_history(conversation_id)
            )
            return result
        except Exception as e:
            self.logger.error(f"Error getting conversation history: {str(e)}")
            return []
    
    def clear_conversation(self, conversation_id: str) -> bool:
        """Clear conversation history."""
        try:
            self._run_async(
                self.chat_service.clear_conversation(conversation_id)
            )
            self.logger.info(f"Conversation cleared: {conversation_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error clearing conversation: {str(e)}")
            return False
    
    # ========================================================================
    # KNOWLEDGE BASE / RAG OPERATIONS
    # ========================================================================
    
    def search_knowledge_base(
        self,
        query: str,
        top_k: int = 5,
    ) -> Optional[List[Dict[str, Any]]]:
        """Search the knowledge base using RAG."""
        try:
            result = self._run_async(
                self.rag_service.search_knowledge_base(query=query, top_k=top_k)
            )
            self.logger.info(f"Knowledge base search returned {len(result) if result else 0} results")
            return result or []
        except Exception as e:
            self.logger.error(f"Error searching knowledge base: {str(e)}")
            return []
    
    # ========================================================================
    # FEEDBACK OPERATIONS
    # ========================================================================
    
    def submit_feedback(
        self,
        conversation_id: str,
        message_id: str,
        rating: int,
        feedback_text: Optional[str] = None,
        email: Optional[str] = None,
    ) -> bool:
        """Submit feedback for a message."""
        try:
            feedback_id = self._run_async(
                self.feedback_service.save_feedback(
                    conversation_id=conversation_id,
                    message_id=message_id,
                    rating=rating,
                    feedback_text=feedback_text,
                    email=email,
                )
            )
            self.logger.info(f"Feedback saved: {feedback_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error submitting feedback: {str(e)}")
            return False
    
    def get_feedback_stats(self) -> Optional[Dict[str, Any]]:
        """Get feedback statistics."""
        try:
            result = self._run_async(
                self.feedback_service.get_feedback_statistics()
            )
            return result
        except Exception as e:
            self.logger.error(f"Error getting feedback stats: {str(e)}")
            return None
    
    # ========================================================================
    # AGENT OPERATIONS
    # ========================================================================
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List available agents."""
        try:
            agents = list(self.agent_service.agents.values())
            self.logger.info(f"Listed {len(agents)} agents")
            return agents
        except Exception as e:
            self.logger.error(f"Error listing agents: {str(e)}")
            return []


# Global service interface instance
_service_interface: Optional[ServiceInterface] = None


def get_service_interface() -> ServiceInterface:
    """Get or create the global service interface instance."""
    global _service_interface
    if _service_interface is None:
        _service_interface = ServiceInterface()
    return _service_interface


def initialize_services():
    """Initialize all services. Call once at startup."""
    interface = get_service_interface()
    interface._run_async(interface.initialize())
