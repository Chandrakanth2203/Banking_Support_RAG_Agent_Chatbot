"""
Embedding Module for RAG System.
Handles embedding generation using pre-trained models.
"""

import logging
from typing import List, Dict, Any
import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generates embeddings for text chunks."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embedding generator.
        
        Args:
            model_name (str): Name of pre-trained embedding model
                Default: all-MiniLM-L6-v2 (fast, good quality)
                Other options: all-mpnet-base-v2 (slower but better)
        """
        self.model_name = model_name
        self.model = None
        self.logger = logger
        self._load_model()
    
    def _load_model(self):
        """Load the embedding model."""
        try:
            from sentence_transformers import SentenceTransformer
            self.logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            self.logger.info(f"Embedding dimension: {self.embedding_dim}")
        except ImportError:
            self.logger.error("sentence-transformers not installed. Install with: pip install sentence-transformers")
            raise
        except Exception as e:
            self.logger.error(f"Error loading embedding model: {str(e)}")
            raise
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts (List[str]): List of text chunks
            
        Returns:
            np.ndarray: Array of embeddings (n_samples, embedding_dim)
        """
        if not texts:
            return np.array([])
        
        try:
            self.logger.info(f"Generating embeddings for {len(texts)} texts")
            embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
            self.logger.info(f"Generated embeddings with shape: {embeddings.shape}")
            return embeddings
        except Exception as e:
            self.logger.error(f"Error generating embeddings: {str(e)}")
            raise
    
    def generate_single_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text (str): Text to embed
            
        Returns:
            np.ndarray: Embedding vector
        """
        if not text:
            return np.zeros(self.embedding_dim)
        
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            self.logger.error(f"Error generating single embedding: {str(e)}")
            raise
    
    def normalize_embeddings(self, embeddings: np.ndarray) -> np.ndarray:
        """
        Normalize embeddings to unit vectors (for cosine similarity).
        
        Args:
            embeddings (np.ndarray): Array of embeddings
            
        Returns:
            np.ndarray: Normalized embeddings
        """
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        normalized = embeddings / (norms + 1e-8)
        return normalized
    
    def get_embedding_dimension(self) -> int:
        """Get the embedding dimension."""
        return self.embedding_dim if self.model else 0
