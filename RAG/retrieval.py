"""
Retrieval Module for RAG System.
Handles query preprocessing and similarity search.
"""

import logging
from typing import List, Dict, Any, Optional
import re

logger = logging.getLogger(__name__)


class Retriever:
    """Retrieves relevant documents based on query similarity with re-ranking."""
    
    def __init__(self, embedding_generator, vector_store, use_reranker: bool = True):
        """
        Initialize retriever.
        
        Args:
            embedding_generator: EmbeddingGenerator instance
            vector_store: VectorStore instance
            use_reranker (bool): Whether to use cross-encoder for re-ranking
        """
        self.embedding_generator = embedding_generator
        self.vector_store = vector_store
        self.use_reranker = use_reranker
        self.reranker = None
        self.logger = logger
        
        if use_reranker:
            self._init_reranker()
    
    def _init_reranker(self):
        """Initialize cross-encoder for result re-ranking."""
        try:
            from sentence_transformers import CrossEncoder
            
            # Use a lightweight cross-encoder model
            model_name = "cross-encoder/mmarco-MiniLMv2-L12-H384-v1"
            self.reranker = CrossEncoder(model_name)
            self.logger.info(f"Initialized reranker with model: {model_name}")
            
        except ImportError:
            self.logger.warning("sentence-transformers not available for cross-encoder re-ranking")
            self.reranker = None
            self.use_reranker = False
        except Exception as e:
            self.logger.error(f"Error initializing reranker: {str(e)}")
            self.reranker = None
            self.use_reranker = False
    
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
            
            # Re-rank results if enabled
            if self.use_reranker and self.reranker and results:
                results = self._rerank_results(processed_query, results, top_k)
            
            self.logger.info(f"Retrieved {len(results)} results")
            return results
            
        except Exception as e:
            self.logger.error(f"Error retrieving: {str(e)}")
            return []
    
    def _rerank_results(
        self,
        query: str,
        initial_results: List[Dict[str, Any]],
        top_k: int
    ) -> List[Dict[str, Any]]:
        """
        Re-rank retrieval results using cross-encoder for better relevance.
        
        Args:
            query (str): Original query
            initial_results (List[Dict]): Results from vector search
            top_k (int): Number of results to return after re-ranking
            
        Returns:
            List[Dict]: Re-ranked results
        """
        try:
            if not initial_results:
                return initial_results
            
            # Prepare pairs for cross-encoder
            pairs = [
                [query, result.get("content", "")]
                for result in initial_results
            ]
            
            # Score with cross-encoder
            scores = self.reranker.predict(pairs)
            
            # Add reranker scores to results
            for result, score in zip(initial_results, scores):
                # Store both original vector similarity and reranker score
                result["reranker_score"] = float(score)
                # Combine scores (weighted average)
                original_score = result.get("relevance_score", 0)
                result["combined_score"] = 0.4 * original_score + 0.6 * (score / 10.0)  # Normalize reranker score
            
            # Sort by combined score
            reranked = sorted(initial_results, key=lambda x: x.get("combined_score", 0), reverse=True)
            
            # Return top-k
            final_results = reranked[:top_k]
            
            self.logger.info(f"Re-ranked {len(initial_results)} results, returning top {len(final_results)}")
            return final_results
            
        except Exception as e:
            self.logger.error(f"Error re-ranking results: {str(e)}")
            # Return original results if re-ranking fails
            return initial_results[:top_k]
    
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
