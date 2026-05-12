"""
LLM AI Agent with Short-Term Memory and Tool Calling.
Provides intelligent response generation with memory management and calculator tools.

Features:
- Short-term memory: Maintains conversation context
- Tool calling: Executes calculator tools for financial calculations
- Interest rate calculations: Simple, compound interest, and EMI calculations
- Extensible tool system: Easy to add new tools
"""

import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, field
from collections import deque

logger = logging.getLogger(__name__)


@dataclass
class MemoryEntry:
    """Represents a single memory entry in conversation history."""
    timestamp: str
    role: str  # "user" or "assistant"
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class ShortTermMemory:
    """
    Short-term memory manager for conversation context.
    Maintains a sliding window of recent messages.
    """
    
    def __init__(self, max_size: int = 10):
        """
        Initialize short-term memory.
        
        Args:
            max_size (int): Maximum number of messages to store
        """
        self.max_size = max_size
        self.memory: deque = deque(maxlen=max_size)
        self.logger = logger
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a message to memory.
        
        Args:
            role (str): "user" or "assistant"
            content (str): Message content
            metadata (Dict): Optional metadata
        """
        entry = MemoryEntry(
            timestamp=datetime.now().isoformat(),
            role=role,
            content=content,
            metadata=metadata or {}
        )
        self.memory.append(entry)
        self.logger.info(f"Added {role} message to memory. Current size: {len(self.memory)}/{self.max_size}")
    
    def get_context(self, num_messages: Optional[int] = None) -> str:
        """
        Get formatted context from memory.
        
        Args:
            num_messages (int): Number of recent messages to retrieve
            
        Returns:
            str: Formatted conversation context
        """
        if not self.memory:
            return ""
        
        messages_to_show = list(self.memory)
        if num_messages:
            messages_to_show = messages_to_show[-num_messages:]
        
        context = "\n".join([
            f"[{entry.timestamp}] {entry.role.upper()}: {entry.content}"
            for entry in messages_to_show
        ])
        
        return context
    
    def get_messages_list(self) -> List[Dict[str, str]]:
        """Get memory as list of message dicts for LLM context."""
        return [
            {
                "role": entry.role,
                "content": entry.content,
                "timestamp": entry.timestamp
            }
            for entry in self.memory
        ]
    
    def clear(self) -> None:
        """Clear all memory."""
        self.memory.clear()
        self.logger.info("Memory cleared")
    
    def get_size(self) -> int:
        """Get current memory size."""
        return len(self.memory)


class CalculatorTools:
    """Calculator tools for financial calculations."""
    
    def __init__(self):
        """Initialize calculator tools."""
        self.logger = logger
    
    def simple_interest(self, principal: float, rate: float, time: float) -> Dict[str, Any]:
        """
        Calculate simple interest.
        
        Args:
            principal (float): Principal amount
            rate (float): Interest rate (annual, in %)
            time (float): Time period (in years)
            
        Returns:
            Dict: Calculation result with interest and total amount
        """
        try:
            interest = (principal * rate * time) / 100
            total_amount = principal + interest
            
            result = {
                "tool": "simple_interest",
                "principal": principal,
                "rate": rate,
                "time": time,
                "interest": round(interest, 2),
                "total_amount": round(total_amount, 2),
                "formula": "SI = (P × R × T) / 100",
                "success": True
            }
            
            self.logger.info(f"Simple Interest Calculated: Principal={principal}, Rate={rate}%, Time={time}yr, SI={interest}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error calculating simple interest: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def compound_interest(self, principal: float, rate: float, time: float, compounds_per_year: int = 1) -> Dict[str, Any]:
        """
        Calculate compound interest.
        
        Args:
            principal (float): Principal amount
            rate (float): Interest rate (annual, in %)
            time (float): Time period (in years)
            compounds_per_year (int): Compounding frequency (1=annually, 2=semi-annually, 4=quarterly, 12=monthly)
            
        Returns:
            Dict: Calculation result
        """
        try:
            amount = principal * (1 + (rate / (100 * compounds_per_year))) ** (compounds_per_year * time)
            interest = amount - principal
            
            result = {
                "tool": "compound_interest",
                "principal": principal,
                "rate": rate,
                "time": time,
                "compounds_per_year": compounds_per_year,
                "interest": round(interest, 2),
                "total_amount": round(amount, 2),
                "formula": "A = P(1 + r/(n×100))^(n×t)",
                "success": True
            }
            
            self.logger.info(f"Compound Interest Calculated: Interest={interest}, Amount={amount}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error calculating compound interest: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def emi_calculation(self, principal: float, annual_rate: float, months: int) -> Dict[str, Any]:
        """
        Calculate EMI (Equated Monthly Installment).
        
        Args:
            principal (float): Loan amount
            annual_rate (float): Annual interest rate (in %)
            months (int): Loan tenure (in months)
            
        Returns:
            Dict: EMI and total interest calculation
        """
        try:
            monthly_rate = annual_rate / (12 * 100)
            
            if monthly_rate == 0:
                emi = principal / months
            else:
                emi = principal * (monthly_rate * (1 + monthly_rate) ** months) / ((1 + monthly_rate) ** months - 1)
            
            total_amount = emi * months
            total_interest = total_amount - principal
            
            result = {
                "tool": "emi_calculation",
                "principal": principal,
                "annual_rate": annual_rate,
                "monthly_rate": round(monthly_rate * 100, 4),
                "months": months,
                "emi": round(emi, 2),
                "total_amount": round(total_amount, 2),
                "total_interest": round(total_interest, 2),
                "formula": "EMI = P × [r(1+r)^n] / [(1+r)^n - 1]",
                "success": True
            }
            
            self.logger.info(f"EMI Calculated: EMI={emi}, Total Interest={total_interest}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error calculating EMI: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def rate_of_return(self, initial_investment: float, final_amount: float, time: float) -> Dict[str, Any]:
        """
        Calculate rate of return on investment.
        
        Args:
            initial_investment (float): Initial investment amount
            final_amount (float): Final amount after time period
            time (float): Time period (in years)
            
        Returns:
            Dict: Rate of return calculation
        """
        try:
            profit = final_amount - initial_investment
            annual_rate = (profit / initial_investment / time) * 100
            
            result = {
                "tool": "rate_of_return",
                "initial_investment": initial_investment,
                "final_amount": final_amount,
                "profit": profit,
                "time": time,
                "annual_rate_of_return": round(annual_rate, 2),
                "formula": "ROR = (Profit / Initial Investment / Time) × 100",
                "success": True
            }
            
            self.logger.info(f"Rate of Return Calculated: {annual_rate}%")
            return result
            
        except Exception as e:
            self.logger.error(f"Error calculating rate of return: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available calculator tools."""
        return [
            {
                "name": "simple_interest",
                "description": "Calculate simple interest: SI = (P × R × T) / 100",
                "parameters": {
                    "principal": "Principal amount",
                    "rate": "Annual interest rate (%)",
                    "time": "Time period (years)"
                }
            },
            {
                "name": "compound_interest",
                "description": "Calculate compound interest with flexible compounding",
                "parameters": {
                    "principal": "Principal amount",
                    "rate": "Annual interest rate (%)",
                    "time": "Time period (years)",
                    "compounds_per_year": "Compounding frequency (1=annual, 12=monthly)"
                }
            },
            {
                "name": "emi_calculation",
                "description": "Calculate EMI (Equated Monthly Installment) for loans",
                "parameters": {
                    "principal": "Loan amount",
                    "annual_rate": "Annual interest rate (%)",
                    "months": "Loan tenure (months)"
                }
            },
            {
                "name": "rate_of_return",
                "description": "Calculate rate of return on investment",
                "parameters": {
                    "initial_investment": "Initial investment amount",
                    "final_amount": "Final amount received",
                    "time": "Investment period (years)"
                }
            }
        ]


class LLMAgent:
    """
    LLM AI Agent with Short-Term Memory and Tool Calling.
    Provides intelligent responses with conversation context and calculator capabilities.
    """
    
    def __init__(self, model_name: str = "gpt-4", max_memory_size: int = 10):
        """
        Initialize LLM Agent.
        
        Args:
            model_name (str): LLM model name
            max_memory_size (int): Maximum short-term memory size
        """
        self.model_name = model_name
        self.logger = logger
        
        # Initialize memory and tools
        self.memory = ShortTermMemory(max_size=max_memory_size)
        self.calculator = CalculatorTools()
        
        # Tool registry
        self.tools: Dict[str, Callable] = {
            "simple_interest": self.calculator.simple_interest,
            "compound_interest": self.calculator.compound_interest,
            "emi_calculation": self.calculator.emi_calculation,
            "rate_of_return": self.calculator.rate_of_return,
        }
        
        self.logger.info(f"LLM Agent initialized with model: {model_name}")
        self.logger.info(f"Memory capacity: {max_memory_size} messages")
        self.logger.info(f"Available tools: {list(self.tools.keys())}")
    
    def call_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Call a calculator tool.
        
        Args:
            tool_name (str): Name of the tool
            **kwargs: Tool parameters
            
        Returns:
            Dict: Tool execution result
        """
        try:
            if tool_name not in self.tools:
                return {
                    "success": False,
                    "error": f"Unknown tool: {tool_name}",
                    "available_tools": list(self.tools.keys())
                }
            
            self.logger.info(f"Calling tool: {tool_name} with args: {kwargs}")
            result = self.tools[tool_name](**kwargs)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error calling tool {tool_name}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def process_query(self, user_query: str, use_tools: bool = True) -> Dict[str, Any]:
        """
        Process user query and generate response with memory context.
        
        Args:
            user_query (str): User's question or request
            use_tools (bool): Whether to attempt tool usage
            
        Returns:
            Dict: Agent response with reasoning
        """
        try:
            self.logger.info(f"\n{'='*80}")
            self.logger.info(f"PROCESSING QUERY: {user_query}")
            self.logger.info(f"{'='*80}")
            
            # Add user query to memory
            self.memory.add_message("user", user_query)
            
            # Get current context from memory
            context = self.memory.get_context(num_messages=5)
            
            self.logger.info(f"\nCurrent Memory Context:\n{context}")
            
            # Check if query requires tool calling
            tool_result = None
            if use_tools:
                tool_result = self._attempt_tool_call(user_query)
            
            # Generate response
            response = self._generate_response(user_query, context, tool_result)
            
            # Add response to memory
            self.memory.add_message("assistant", response["content"], metadata={"tool_used": tool_result is not None})
            
            self.logger.info(f"\nAgent Response:\n{response['content']}")
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing query: {str(e)}")
            return {
                "content": f"Error processing your query: {str(e)}",
                "success": False,
                "error": str(e)
            }
    
    def _attempt_tool_call(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Attempt to identify and call appropriate tools based on query.
        
        Args:
            query (str): User query
            
        Returns:
            Dict: Tool result or None if no tool applies
        """
        query_lower = query.lower()
        
        # Simple interest keywords
        if any(keyword in query_lower for keyword in ["simple interest", "si", "basic interest"]):
            self.logger.info("Detected simple interest query")
            return self.calculator.simple_interest(
                principal=1000,  # Default value - would be extracted from query
                rate=5,          # Default value
                time=2           # Default value
            )
        
        # Compound interest keywords
        elif any(keyword in query_lower for keyword in ["compound interest", "ci", "compounded"]):
            self.logger.info("Detected compound interest query")
            return self.calculator.compound_interest(
                principal=1000,
                rate=5,
                time=2
            )
        
        # EMI keywords
        elif any(keyword in query_lower for keyword in ["emi", "loan", "installment", "equated monthly"]):
            self.logger.info("Detected EMI calculation query")
            return self.calculator.emi_calculation(
                principal=100000,
                annual_rate=8,
                months=60
            )
        
        # Rate of return keywords
        elif any(keyword in query_lower for keyword in ["rate of return", "ror", "return on investment", "roi"]):
            self.logger.info("Detected rate of return query")
            return self.calculator.rate_of_return(
                initial_investment=10000,
                final_amount=15000,
                time=2
            )
        
        self.logger.info("No matching tool identified for query")
        return None
    
    def _generate_response(self, query: str, context: str, tool_result: Optional[Dict[str, Any]]) -> Dict[str, str]:
        """
        Generate agent response with context and tool results.
        
        Args:
            query (str): User query
            context (str): Memory context
            tool_result (Dict): Result from tool call if any
            
        Returns:
            Dict: Generated response
        """
        response_text = f"""I'm an intelligent banking support agent with access to financial calculation tools.

Based on your query: "{query}"

"""
        
        if tool_result and tool_result.get("success"):
            response_text += f"""I've performed a financial calculation for you:

Tool Used: {tool_result.get('tool')}
Formula: {tool_result.get('formula')}

Calculation Details:
"""
            # Format tool result details
            for key, value in tool_result.items():
                if key not in ['tool', 'formula', 'success']:
                    response_text += f"- {key.replace('_', ' ').title()}: {value}\n"
        else:
            response_text += """I can help you with various financial calculations including:
- Simple Interest Calculation
- Compound Interest Calculation
- EMI (Equated Monthly Installment) Calculation
- Rate of Return on Investment

Feel free to ask for any of these calculations with the required details!
"""
        
        response_text += f"\n\nConversation Memory (last 5 messages): {len(self.memory.memory)} messages stored"
        
        return {
            "content": response_text,
            "model": self.model_name,
            "tool_used": tool_result is not None,
            "success": True,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_memory_status(self) -> Dict[str, Any]:
        """Get current memory status."""
        return {
            "memory_size": self.memory.get_size(),
            "max_memory_size": self.memory.max_size,
            "messages": self.memory.get_messages_list(),
            "available_tools": list(self.tools.keys()),
        }
    
    def clear_memory(self) -> None:
        """Clear conversation memory."""
        self.memory.clear()
        self.logger.info("Agent memory cleared")
    
    def get_tools_info(self) -> List[Dict[str, Any]]:
        """Get information about available tools."""
        return self.calculator.get_available_tools()
