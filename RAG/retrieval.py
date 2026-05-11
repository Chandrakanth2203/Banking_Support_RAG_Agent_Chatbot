"""
Retrieval Module for RAG System.
Handles query preprocessing and similarity search.
"""

import logging
from typing import List, Dict, Any, Optional
import re

logger = logging.getLogger(__name__)


class Retriever:
    """Retrieves relevant documents based on query similarity."""
    
    def __init__(self, embedding_generator, vector_store):
        """
        Initialize retriever.
        
        Args:
            embedding_generator: EmbeddingGenerator instance
            vector_store: VectorStore instance
        """
        self.embedding_generator = embedding_generator
        self.vector_store = vector_store
        self.logger = logger
    
    def preprocess_query(self, query: str) -> str:
        """
        Preprocess query for better retrieval.
        
        Args:
            query (str): Raw user query
            
        Returns:
            str: Preprocessed query
        """
        # Remove extra whitespace
        query = re.sub(r'\s+', ' ', query).strip()
        
        # Lowercase (optional, depends on model)
        # query = query.lower()
        
        return query
    
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        category_filter: Optional[str] = None,
        source_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query (str): User query
            top_k (int): Number of results to return
            category_filter (str): Filter by document category
            source_filter (str): Filter by document source
            
        Returns:
            List[Dict]: List of relevant chunks ranked by relevance
        """
        try:
            # Preprocess query
            processed_query = self.preprocess_query(query)
            self.logger.info(f"Retrieving for query: {processed_query}")
            
            # Generate query embedding
            query_embedding = self.embedding_generator.generate_single_embedding(processed_query)
            
            # Build filters
            filters = {}
            if category_filter:
                filters["category"] = category_filter
            if source_filter:
                filters["source"] = source_filter
            
            # Search vector store
            results = self.vector_store.search(
                query_embedding=query_embedding,
                top_k=top_k,
                filters=filters if filters else None
            )
            
            self.logger.info(f"Retrieved {len(results)} results")
            return results
            
        except Exception as e:
            self.logger.error(f"Error retrieving: {str(e)}")
            return []
    
    def retrieve_by_source(
        self,
        query: str,
        top_k: int = 5,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Retrieve results grouped by source document.
        
        Args:
            query (str): User query
            top_k (int): Number of results per source
            
        Returns:
            Dict: Results grouped by source
        """
        try:
            results = self.retrieve(query, top_k * 3)  # Get more to group
            
            grouped = {}
            for result in results:
                source = result.get("source", "Unknown")
                if source not in grouped:
                    grouped[source] = []
                
                if len(grouped[source]) < top_k:
                    grouped[source].append(result)
            
            return grouped
            
        except Exception as e:
            self.logger.error(f"Error retrieving by source: {str(e)}")
            return {}
    
    def retrieve_with_context(
        self,
        query: str,
        top_k: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve results with additional context.
        
        Args:
            query (str): User query
            top_k (int): Number of results to return
            
        Returns:
            List[Dict]: Results with context information
        """
        results = self.retrieve(query, top_k)
        
        for result in results:
            # Add ranking info
            result["rank"] = results.index(result) + 1
            
            # Add context summary
            content = result.get("content", "")
            result["summary"] = self._create_summary(content)
        
        return results
    
    def _create_summary(self, text: str, max_length: int = 100) -> str:
        """
        Create a brief summary of the text.
        
        Args:
            text (str): Full text
            max_length (int): Maximum summary length
            
        Returns:
            str: Summary
        """
        if len(text) <= max_length:
            return text
        
        # Find a good break point (end of sentence)
        summary = text[:max_length]
        last_period = summary.rfind('.')
        
        if last_period > max_length // 2:
            summary = summary[:last_period + 1]
        else:
            summary = summary + "..."
        
        return summary
