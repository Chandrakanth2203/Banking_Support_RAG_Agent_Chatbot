"""
Agent Service for Banking Support AI Agent Chatbot API.
Handles multi-agent routing and response generation with LLM capabilities.
"""

import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Add root path to sys.path for RAG imports
root_path = Path(__file__).parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

# Import LLMAgent for financial calculations
try:
    from RAG import LLMAgent
    LLMAGENT_AVAILABLE = True
except ImportError:
    LLMAGENT_AVAILABLE = False
    logger.warning("LLMAgent not available - financial calculations will be disabled")


class AgentService:
    """Service for multi-agent system."""
    
    def __init__(self):
        """Initialize the agent service."""
        self.logger = logger
        
        # Initialize LLM Agent for financial calculations if available
        self.llm_agent = None
        if LLMAGENT_AVAILABLE:
            try:
                self.llm_agent = LLMAgent()
                self.logger.info("LLMAgent initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize LLMAgent: {str(e)}")
        
        self.agents = {
            "general_support": {
                "agent_type": "general_support",
                "name": "General Support Agent",
                "description": "Handles general inquiries and support requests",
                "capabilities": ["answer_questions", "provide_information"],
                "is_available": True,
            },
            "account_management": {
                "agent_type": "account_management",
                "name": "Account Management Agent",
                "description": "Handles account-related queries and operations",
                "capabilities": ["account_info", "transactions", "account_settings"],
                "is_available": True,
            },
            "loan_agent": {
                "agent_type": "loan_agent",
                "name": "Loan Agent",
                "description": "Handles loan inquiries and applications",
                "capabilities": ["loan_info", "application_status", "eligibility_check"],
                "is_available": True,
            },
            "complaint_resolution": {
                "agent_type": "complaint_resolution",
                "name": "Complaint Resolution Agent",
                "description": "Handles customer complaints and escalations",
                "capabilities": ["complaint_filing", "status_tracking", "escalation"],
                "is_available": True,
            },
            "financial_calculator": {
                "agent_type": "financial_calculator",
                "name": "Financial Calculator Agent",
                "description": "Performs financial calculations with memory management",
                "capabilities": [
                    "simple_interest",
                    "compound_interest",
                    "emi_calculation",
                    "rate_of_return"
                ],
                "is_available": LLMAGENT_AVAILABLE,
            },
        }
    
    async def route_to_agent(
        self,
        message: str,
        rag_results: List[Dict[str, Any]],
        conversation_id: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> Dict[str, Any]:
        """Route message to appropriate agent and generate response."""
        message_lower = message.lower()
        
        # Determine agent based on query content
        agent_type = await self._determine_agent(message_lower, rag_results)
        
        # Generate response using appropriate agent
        response = await self._generate_agent_response(
            agent_type=agent_type,
            message=message,
            rag_results=rag_results,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        return response
    
    async def _determine_agent(
        self,
        message: str,
        rag_results: List[Dict[str, Any]],
    ) -> str:
        """Determine which agent should handle the request."""
        keywords = {
            "financial_calculator": [
                "simple interest",
                "compound interest",
                "emi",
                "equated monthly",
                "rate of return",
                "roi",
                "interest",
                "loan",
                "installment",
            ],
            "loan_agent": ["loan", "credit", "borrowing", "eligibility"],
            "account_management": ["account", "balance", "transfer", "transaction", "password"],
            "complaint_resolution": ["complaint", "issue", "problem", "escalate"],
        }
        
        # Check keywords in message (prioritize financial calculator)
        for agent, words in keywords.items():
            if any(word in message for word in words):
                # Financial calculator has priority for financial keywords
                if agent == "financial_calculator" and LLMAGENT_AVAILABLE:
                    return agent
                elif agent != "financial_calculator":
                    return agent
        
        # Check categories in RAG results
        if rag_results:
            for result in rag_results:
                category = result.get("category", "").lower()
                if "loan" in category:
                    return "loan_agent"
                elif "account" in category:
                    return "account_management"
                elif "complaint" in category:
                    return "complaint_resolution"
        
        # Default to general support
        return "general_support"
    
    async def _generate_agent_response(
        self,
        agent_type: str,
        message: str,
        rag_results: List[Dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> Dict[str, Any]:
        """Generate response from specific agent."""
        
        # Handle financial calculator agent
        if agent_type == "financial_calculator" and self.llm_agent:
            try:
                llm_response = self.llm_agent.process_query(message, use_tools=True)
                
                return {
                    "agent_type": agent_type,
                    "content": llm_response.get("content", ""),
                    "tool_used": llm_response.get("tool_used", False),
                    "confidence": 0.95 if llm_response.get("success") else 0.5,
                    "timestamp": datetime.now().isoformat(),
                    "model": llm_response.get("model", "gpt-4"),
                }
            except Exception as e:
                self.logger.error(f"Error in financial calculator agent: {str(e)}")
                return {
                    "agent_type": agent_type,
                    "content": f"Error processing financial calculation: {str(e)}",
                    "confidence": 0.0,
                    "timestamp": datetime.now().isoformat(),
                    "error": str(e),
                }
        
        # Build response from RAG results if available for other agents
        response_text = ""
        
        if rag_results:
            response_text = "Based on our knowledge base:\n\n"
            for idx, result in enumerate(rag_results, 1):
                response_text += f"{idx}. **{result['title']}**: {result['content']}\n"
        else:
            response_text = self._get_default_response(agent_type, message)
        
        confidence = len(rag_results) / 5.0 if rag_results else 0.5
        
        self.logger.info(f"Generated response from {agent_type} agent")
        
        return {
            "agent_type": agent_type,
            "content": response_text,
            "confidence": min(confidence, 1.0),
            "timestamp": datetime.now().isoformat(),
        }
    
    def _get_default_response(self, agent_type: str, message: str) -> str:
        """Get default response for agent when no RAG results."""
        responses = {
            "financial_calculator": (
                "I'm a financial calculation assistant. I can help you with:\n"
                "- Simple Interest Calculation: SI = (P × R × T) / 100\n"
                "- Compound Interest: A = P(1 + r/(n×100))^(n×t)\n"
                "- EMI Calculation: EMI = P × [r(1+r)^n] / [(1+r)^n - 1]\n"
                "- Rate of Return: ROR = (Profit / Initial Investment / Time) × 100\n\n"
                f"Your question: {message}\n\n"
                "Please provide the necessary parameters for calculation."
            ),
            "loan_agent": (
                "Thank you for your inquiry about loans. I can help you with:\n"
                "- Information about different loan types\n"
                "- Eligibility criteria\n"
                "- Application process\n"
                "- Current interest rates\n\n"
                f"Your question: {message}\n\n"
                "Could you please provide more details so I can assist you better?"
            ),
            "account_management": (
                "I can help you with account-related matters such as:\n"
                "- Checking your balance\n"
                "- Setting up transfers\n"
                "- Password reset\n"
                "- Transaction history\n\n"
                f"Your question: {message}\n\n"
                "What specific information do you need?"
            ),
            "complaint_resolution": (
                "I'm sorry to hear you're experiencing an issue. I can help you:\n"
                "- File a complaint\n"
                "- Track existing complaints\n"
                "- Escalate to senior support\n\n"
                f"Your concern: {message}\n\n"
                "Please provide more details so we can resolve this quickly."
            ),
            "general_support": (
                "Thank you for contacting Banking Support AI Agent Chatbot.\n\n"
                f"Your question: {message}\n\n"
                "I'm here to help! Please let me know what you need assistance with."
            ),
        }
        
        return responses.get(agent_type, responses["general_support"])
    
    async def list_available_agents(self) -> List[Dict[str, Any]]:
        """List all available agents."""
        return [agent for agent in self.agents.values() if agent["is_available"]]
    
    async def get_agent_info(self, agent_type: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific agent."""
        return self.agents.get(agent_type)
