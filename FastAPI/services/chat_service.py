"""
Chat Service for Banking Support AI Agent Chatbot API.
Handles conversation management and message storage.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class ChatService:
    """Service for managing chat conversations."""
    
    def __init__(self):
        """Initialize the chat service."""
        self.conversations: Dict[str, Dict[str, Any]] = {}
        self.logger = logger
    
    async def initialize(self):
        """Initialize the service (load from database if needed)."""
        self.logger.info("ChatService initialized")
        # In production, load from database
        pass
    
    async def cleanup(self):
        """Cleanup resources."""
        self.logger.info("ChatService cleanup")
        pass
    
    async def get_or_create_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """Get or create a conversation."""
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = {
                "conversation_id": conversation_id,
                "created_at": datetime.now().isoformat(),
                "messages": [],
                "metadata": {},
            }
            self.logger.info(f"Created new conversation: {conversation_id}")
        
        return self.conversations[conversation_id]
    
    async def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add a message to a conversation."""
        conversation = await self.get_or_create_conversation(conversation_id)
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
        }
        
        conversation["messages"].append(message)
        self.logger.info(
            f"Added {role} message to conversation {conversation_id}: {content[:50]}..."
        )
    
    async def get_conversation_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get conversation history."""
        if conversation_id in self.conversations:
            return self.conversations[conversation_id]["messages"]
        return []
    
    async def clear_conversation(self, conversation_id: str) -> None:
        """Clear a conversation."""
        if conversation_id in self.conversations:
            self.conversations[conversation_id]["messages"] = []
            self.logger.info(f"Cleared conversation: {conversation_id}")
    
    async def get_active_conversation_count(self) -> int:
        """Get count of active conversations."""
        return len(self.conversations)
    
    async def get_total_messages_processed(self) -> int:
        """Get total messages processed."""
        total = 0
        for conversation in self.conversations.values():
            total += len(conversation["messages"])
        return total
