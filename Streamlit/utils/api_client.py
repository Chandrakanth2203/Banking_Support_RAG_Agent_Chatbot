"""
API Client for Banking Support AI Agent Chatbot.
Handles communication with FastAPI backend.
"""

import requests
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class ChatbotAPIClient:
    """Client for communicating with the Banking Support AI Agent Chatbot API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the API client."""
        self.base_url = base_url
        self.session = requests.Session()
        self.logger = logger
    
    def health_check(self) -> bool:
        """Check if API is healthy."""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return False
    
    # ========================================================================
    # CHAT METHODS
    # ========================================================================
    
    def send_message(
        self,
        conversation_id: str,
        message: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        model: str = "gpt-4",
    ) -> Optional[Dict[str, Any]]:
        """Send a message to the chatbot."""
        try:
            payload = {
                "conversation_id": conversation_id,
                "message": message,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "model": model,
            }
            
            response = self.session.post(
                f"{self.base_url}/chat",
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            
            self.logger.info(f"Message sent successfully for conversation: {conversation_id}")
            return response.json()
        except Exception as e:
            self.logger.error(f"Error sending message: {str(e)}")
            return None
    
    def get_conversation_history(self, conversation_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get conversation history."""
        try:
            payload = {"conversation_id": conversation_id}
            response = self.session.post(
                f"{self.base_url}/chat/history",
                json=payload,
                timeout=10,
            )
            response.raise_for_status()
            
            data = response.json()
            self.logger.info(f"Retrieved history for conversation: {conversation_id}")
            return data.get("messages", [])
        except Exception as e:
            self.logger.error(f"Error getting conversation history: {str(e)}")
            return []
    
    def clear_conversation(self, conversation_id: str) -> bool:
        """Clear conversation history."""
        try:
            response = self.session.delete(
                f"{self.base_url}/chat/conversation/{conversation_id}",
                timeout=10,
            )
            response.raise_for_status()
            
            self.logger.info(f"Conversation cleared: {conversation_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error clearing conversation: {str(e)}")
            return False
    
    # ========================================================================
    # KNOWLEDGE BASE METHODS
    # ========================================================================
    
    def search_knowledge_base(
        self,
        query: str,
        top_k: int = 5,
    ) -> Optional[List[Dict[str, Any]]]:
        """Search the knowledge base."""
        try:
            payload = {
                "query": query,
                "top_k": top_k,
            }
            
            response = self.session.post(
                f"{self.base_url}/knowledge-base/search",
                json=payload,
                timeout=10,
            )
            response.raise_for_status()
            
            data = response.json()
            self.logger.info(f"Knowledge base search for '{query}' returned {len(data.get('results', []))} results")
            return data.get("results", [])
        except Exception as e:
            self.logger.error(f"Error searching knowledge base: {str(e)}")
            return []
    
    def get_kb_stats(self) -> Optional[Dict[str, Any]]:
        """Get knowledge base statistics."""
        try:
            response = self.session.get(
                f"{self.base_url}/knowledge-base/stats",
                timeout=10,
            )
            response.raise_for_status()
            
            self.logger.info("Retrieved knowledge base statistics")
            return response.json()
        except Exception as e:
            self.logger.error(f"Error getting KB stats: {str(e)}")
            return None
    
    # ========================================================================
    # FEEDBACK METHODS
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
            payload = {
                "conversation_id": conversation_id,
                "message_id": message_id,
                "rating": rating,
                "feedback_text": feedback_text,
                "email": email,
            }
            
            response = self.session.post(
                f"{self.base_url}/feedback",
                json=payload,
                timeout=10,
            )
            response.raise_for_status()
            
            self.logger.info(f"Feedback submitted for conversation: {conversation_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error submitting feedback: {str(e)}")
            return False
    
    def get_feedback_stats(self) -> Optional[Dict[str, Any]]:
        """Get feedback statistics."""
        try:
            response = self.session.get(
                f"{self.base_url}/feedback/statistics",
                timeout=10,
            )
            response.raise_for_status()
            
            self.logger.info("Retrieved feedback statistics")
            return response.json()
        except Exception as e:
            self.logger.error(f"Error getting feedback stats: {str(e)}")
            return None
    
    # ========================================================================
    # AGENT METHODS
    # ========================================================================
    
    def list_agents(self) -> Optional[List[Dict[str, Any]]]:
        """List available agents."""
        try:
            response = self.session.get(
                f"{self.base_url}/agents",
                timeout=10,
            )
            response.raise_for_status()
            
            data = response.json()
            self.logger.info(f"Retrieved {data.get('total_agents', 0)} agents")
            return data.get("agents", [])
        except Exception as e:
            self.logger.error(f"Error listing agents: {str(e)}")
            return []
    
    # ========================================================================
    # SYSTEM METHODS
    # ========================================================================
    
    def get_system_status(self) -> Optional[Dict[str, Any]]:
        """Get system status."""
        try:
            response = self.session.get(
                f"{self.base_url}/system/status",
                timeout=10,
            )
            response.raise_for_status()
            
            self.logger.info("Retrieved system status")
            return response.json()
        except Exception as e:
            self.logger.error(f"Error getting system status: {str(e)}")
            return None


# Global API client instance
api_client: Optional[ChatbotAPIClient] = None


def get_api_client(base_url: str = "http://localhost:8000") -> ChatbotAPIClient:
    """Get or create API client instance."""
    global api_client
    if api_client is None:
        api_client = ChatbotAPIClient(base_url)
    return api_client
