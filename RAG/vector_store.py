"""
Vector Store Module for RAG System.
Handles storing and retrieving embeddings using FAISS.
"""

import logging
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
import json
from pathlib import Path
import pickle

logger = logging.getLogger(__name__)


class VectorStore:
    """Manages vector embeddings storage and retrieval using FAISS."""
    
    def __init__(self, embedding_dim: int, index_path: Optional[str] = None):
        """
        Initialize vector store.
        
        Args:
            embedding_dim (int): Dimension of embeddings
            index_path (str): Path to save/load FAISS index
        """
        self.embedding_dim = embedding_dim
        self.index_path = index_path
        self.index = None
        self.metadata = []  # Store metadata for each vector
        self.logger = logger
        self._init_index()
    
    def _init_index(self):
        """Initialize FAISS index."""
        try:
            import faiss
            # Use IndexFlatIP for cosine similarity (inner product)
            self.index = faiss.IndexFlatIP(self.embedding_dim)
            self.logger.info(f"Initialized FAISS index with dimension {self.embedding_dim}")
        except ImportError:
            self.logger.error("faiss-cpu not installed. Install with: pip install faiss-cpu")
            raise
    
    def add_embeddings(
        self,
        embeddings: np.ndarray,
        metadata: List[Dict[str, Any]]
    ) -> None:
        """
        Add embeddings to the index.
        
        Args:
            embeddings (np.ndarray): Array of embeddings (n_samples, embedding_dim)
            metadata (List[Dict]): Metadata for each embedding
        """
        if len(embeddings) == 0:
            self.logger.warning("No embeddings to add")
            return
        
        if len(embeddings) != len(metadata):
            raise ValueError("Embeddings and metadata lengths don't match")
        
        try:
            # Normalize embeddings for cosine similarity
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            normalized = embeddings / (norms + 1e-8)
            
            # Add to index
            self.index.add(normalized.astype(np.float32))
            self.metadata.extend(metadata)
            
            self.logger.info(f"Added {len(embeddings)} embeddings to index")
        except Exception as e:
            self.logger.error(f"Error adding embeddings: {str(e)}")
            raise
    
    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar embeddings.
        
        Args:
            query_embedding (np.ndarray): Query embedding vector
            top_k (int): Number of results to return
            filters (Dict): Metadata filters (e.g., category, source)
            
        Returns:
            List[Dict]: List of similar chunks with scores
        """
        if self.index.ntotal == 0:
            self.logger.warning("Vector store is empty")
            return []
        
        try:
            # Normalize query embedding
            norm = np.linalg.norm(query_embedding)
            normalized_query = query_embedding / (norm + 1e-8)
            normalized_query = normalized_query.reshape(1, -1).astype(np.float32)
            
            # Search
            scores, indices = self.index.search(normalized_query, min(top_k * 3, self.index.ntotal))
            
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx == -1:  # Invalid result
                    continue
                
                metadata = self.metadata[idx]
                
                # Apply filters if provided
                if filters:
                    if not self._matches_filters(metadata, filters):
                        continue
                
                results.append({
                    "index": int(idx),
                    "content": metadata.get("content", ""),
                    "source": metadata.get("source", ""),
                    "title": metadata.get("title", ""),
                    "category": metadata.get("category", ""),
                    "chunk_id": metadata.get("chunk_id", 0),
                    "relevance_score": float(score),
                    "metadata": metadata,
                })
                
                if len(results) >= top_k:
                    break
            
            self.logger.info(f"Search returned {len(results)} results")
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching: {str(e)}")
            return []
    
    def _matches_filters(self, metadata: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if metadata matches the filters."""
        for key, value in filters.items():
            if metadata.get(key) != value:
                return False
        return True
    
    def save(self, save_path: str) -> None:
        """
        Save index and metadata to disk.
        
        Args:
            save_path (str): Path to save index
        """
        try:
            import faiss
            
            save_dir = Path(save_path)
            save_dir.mkdir(parents=True, exist_ok=True)
            
            # Save FAISS index
            index_file = save_dir / "faiss_index.bin"
            faiss.write_index(self.index, str(index_file))
            
            # Save metadata
            metadata_file = save_dir / "metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
            
            self.logger.info(f"Saved index and metadata to {save_path}")
        except Exception as e:
            self.logger.error(f"Error saving index: {str(e)}")
            raise
    
    def load(self, load_path: str) -> None:
        """
        Load index and metadata from disk.
        
        Args:
            load_path (str): Path to load index from
        """
        try:
            import faiss
            
            load_dir = Path(load_path)
            
            # Load FAISS index
            index_file = load_dir / "faiss_index.bin"
            if index_file.exists():
                self.index = faiss.read_index(str(index_file))
                self.logger.info(f"Loaded FAISS index from {index_file}")
            
            # Load metadata
            metadata_file = load_dir / "metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    self.metadata = json.load(f)
                self.logger.info(f"Loaded metadata from {metadata_file}")
        except Exception as e:
            self.logger.error(f"Error loading index: {str(e)}")
            raise
    
    def get_size(self) -> int:
        """Get number of embeddings in the index."""
        return self.index.ntotal if self.index else 0
