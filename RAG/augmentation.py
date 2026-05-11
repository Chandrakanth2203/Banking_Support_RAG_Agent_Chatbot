"""
Augmentation Module for RAG System.
Handles context assembly and prompt engineering.
"""

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class ContextAugmentation:
    """Assembles context and creates prompts for LLM."""
    
    def __init__(self, max_context_tokens: int = 2000):
        """
        Initialize context augmentation.
        
        Args:
            max_context_tokens (int): Maximum tokens for context window
        """
        self.max_context_tokens = max_context_tokens
        self.logger = logger
    
    def assemble_context(
        self,
        retrieved_chunks: List[Dict[str, Any]],
    ) -> str:
        """
        Assemble retrieved chunks into context.
        
        Args:
            retrieved_chunks (List[Dict]): Retrieved document chunks
            
        Returns:
            str: Assembled context
        """
        if not retrieved_chunks:
            return ""
        
        context_parts = []
        total_chars = 0
        
        for i, chunk in enumerate(retrieved_chunks, 1):
            source = chunk.get("source", "Unknown")
            title = chunk.get("title", "")
            content = chunk.get("content", "")
            score = chunk.get("relevance_score", 0)
            
            # Create formatted chunk
            chunk_text = f"[Source: {source}]\n{content}"
            
            # Check if adding this chunk exceeds limit
            if total_chars + len(chunk_text) > self.max_context_tokens:
                self.logger.info(f"Context window limit reached at chunk {i}")
                break
            
            context_parts.append(chunk_text)
            total_chars += len(chunk_text)
        
        context = "\n\n---\n\n".join(context_parts)
        self.logger.info(f"Assembled context from {len(context_parts)} chunks (~{total_chars} chars)")
        
        return context
    
    def create_prompt(
        self,
        query: str,
        context: str,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Create a prompt for the LLM.
        
        Args:
            query (str): User query
            context (str): Retrieved context
            system_prompt (str): Custom system prompt
            
        Returns:
            str: Formatted prompt for LLM
        """
        if system_prompt is None:
            system_prompt = self._get_default_system_prompt()
        
        if context:
            prompt = f"""{system_prompt}

Context Information:
{context}

Question: {query}

Please answer based on the context provided above. If the answer is not in the context, state that clearly."""
        else:
            prompt = f"""{system_prompt}

Question: {query}

Note: No context was available for this query."""
        
        return prompt
    
    def _get_default_system_prompt(self) -> str:
        """Get default system prompt."""
        return """You are a helpful Banking Support AI Assistant. Your role is to provide accurate, clear, and concise answers about banking services, policies, and products.

Guidelines:
1. Answer based on the provided context
2. Be professional and courteous
3. If unsure, admit it rather than guess
4. Provide relevant details but keep answers concise
5. When appropriate, suggest next steps or related services"""
    
    def create_prompt_with_citations(
        self,
        query: str,
        retrieved_chunks: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Create a prompt that includes citation information.
        
        Args:
            query (str): User query
            retrieved_chunks (List[Dict]): Retrieved chunks with metadata
            system_prompt (str): Custom system prompt
            
        Returns:
            str: Formatted prompt with citation information
        """
        context = self.assemble_context(retrieved_chunks)
        prompt = self.create_prompt(query, context, system_prompt)
        
        # Add citation guidance
        citation_guide = self._create_citation_guide(retrieved_chunks)
        if citation_guide:
            prompt += f"\n\nSource Information:\n{citation_guide}"
        
        return prompt
    
    def _create_citation_guide(self, retrieved_chunks: List[Dict[str, Any]]) -> str:
        """Create a guide for citing sources."""
        if not retrieved_chunks:
            return ""
        
        citations = []
        for i, chunk in enumerate(retrieved_chunks, 1):
            source = chunk.get("source", "Unknown")
            score = chunk.get("relevance_score", 0)
            citations.append(f"[{i}] {source} (Confidence: {score:.2%})")
        
        return "Sources:\n" + "\n".join(citations)
    
    def estimate_tokens(self, text: str) -> int:
        """
        Rough estimate of tokens in text (1 token ≈ 4 characters).
        
        Args:
            text (str): Text to estimate
            
        Returns:
            int: Estimated token count
        """
        return len(text) // 4
    
    def trim_context(self, context: str, max_tokens: int) -> str:
        """
        Trim context to fit within token limit.
        
        Args:
            context (str): Full context
            max_tokens (int): Maximum tokens
            
        Returns:
            str: Trimmed context
        """
        max_chars = max_tokens * 4
        
        if len(context) <= max_chars:
            return context
        
        # Find last complete section
        trimmed = context[:max_chars]
        last_separator = trimmed.rfind("\n\n---\n\n")
        
        if last_separator > 0:
            trimmed = trimmed[:last_separator]
        
        return trimmed + "\n\n[Context truncated due to length...]"
