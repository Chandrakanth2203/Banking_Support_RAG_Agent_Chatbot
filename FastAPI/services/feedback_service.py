"""
Feedback Service for Banking Support AI Agent Chatbot API.
Handles user feedback collection and analysis.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class FeedbackService:
    """Service for managing user feedback."""
    
    def __init__(self):
        """Initialize the feedback service."""
        self.feedback_records: Dict[str, Dict[str, Any]] = {}
        self.feedback_counter = 0
        self.logger = logger
    
    async def save_feedback(
        self,
        conversation_id: str,
        message_id: str,
        rating: int,
        feedback_text: Optional[str] = None,
        timestamp: Optional[str] = None,
        email: Optional[str] = None,
    ) -> str:
        """Save user feedback."""
        self.feedback_counter += 1
        feedback_id = f"fb_{self.feedback_counter}"
        
        self.feedback_records[feedback_id] = {
            "feedback_id": feedback_id,
            "conversation_id": conversation_id,
            "message_id": message_id,
            "rating": rating,
            "feedback_text": feedback_text,
            "timestamp": timestamp or datetime.now().isoformat(),
            "email": email,
        }
        
        self.logger.info(
            f"Saved feedback {feedback_id}: conversation={conversation_id}, rating={rating}"
        )
        return feedback_id
    
    async def get_feedback_statistics(self) -> Dict[str, Any]:
        """Get feedback statistics."""
        if not self.feedback_records:
            return {
                "total_feedback": 0,
                "average_rating": 0.0,
                "rating_distribution": {},
            }
        
        ratings = [fb["rating"] for fb in self.feedback_records.values()]
        rating_distribution = {}
        
        for rating in ratings:
            rating_distribution[str(rating)] = rating_distribution.get(str(rating), 0) + 1
        
        avg_rating = sum(ratings) / len(ratings) if ratings else 0.0
        
        return {
            "total_feedback": len(self.feedback_records),
            "average_rating": round(avg_rating, 2),
            "rating_distribution": rating_distribution,
            "positive_feedback_percent": round((len([r for r in ratings if r >= 4]) / len(ratings) * 100) if ratings else 0, 2),
        }
    
    async def get_feedback_by_conversation(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get all feedback for a conversation."""
        return [
            fb for fb in self.feedback_records.values()
            if fb["conversation_id"] == conversation_id
        ]
