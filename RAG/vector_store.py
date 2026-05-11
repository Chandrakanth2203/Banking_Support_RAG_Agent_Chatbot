"""
Weaviate Vector Store Module for RAG System.
Handles storing and retrieving embeddings using Weaviate vector database.
"""

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class WeaviateVectorStore:
    """Manages vector embeddings storage and retrieval using Weaviate."""
    
    def __init__(
        self,
        url: str = "http://localhost:8080",
        api_key: Optional[str] = None,
        embedding_dim: int = 384,
        class_name: str = "DocumentChunk"
    ):
        """
        Initialize Weaviate vector store.
        
        Args:
            url (str): Weaviate server URL
            api_key (str): Optional API key for authentication
            embedding_dim (int): Dimension of embeddings
            class_name (str): Weaviate class name for schema
        """
        self.url = url
        self.api_key = api_key
        self.embedding_dim = embedding_dim
        self.class_name = class_name
        self.client = None
        self.logger = logger
        self._init_weaviate()
    
    def _init_weaviate(self):
        """Initialize Weaviate client and create schema."""
        try:
            import weaviate
            
            self.logger.info(f"Connecting to Weaviate at {self.url}")
            
            # Connect to Weaviate
            auth_client_secret = None
            if self.api_key:
                auth_client_secret = weaviate.auth.AuthApiKey(api_key=self.api_key)
            
            self.client = weaviate.Client(
                url=self.url,
                auth_client_secret=auth_client_secret
            )
            
            # Check connection
            if self.client.is_ready():
                self.logger.info("Successfully connected to Weaviate")
            else:
                raise ConnectionError("Weaviate is not ready")
            
            # Create schema if not exists
            self._create_schema()
            
        except ImportError:
            self.logger.error("weaviate-client not installed. Install with: pip install weaviate-client")
            raise
        except Exception as e:
            self.logger.error(f"Error initializing Weaviate: {str(e)}")
            raise
    
    def _create_schema(self):
        """Create Weaviate schema if it doesn't exist."""
        try:
            # Check if class already exists
            if self.client.schema.exists(self.class_name):
                self.logger.info(f"Class {self.class_name} already exists")
                return
            
            # Create schema
            schema = {
                "classes": [
                    {
                        "class": self.class_name,
                        "description": "Document chunks with embeddings for RAG",
                        "vectorizer": "none",  # We provide embeddings
                        "vectorIndexConfig": {
                            "distance": "cosine",
                            "ef": 64,
                            "efConstruction": 128,
                            "maxConnections": 32,
                        },
                        "properties": [
                            {
                                "name": "content",
                                "description": "Text content of the chunk",
                                "dataType": ["text"],
                            },
                            {
                                "name": "source",
                                "description": "Source document",
                                "dataType": ["text"],
                            },
                            {
                                "name": "title",
                                "description": "Document title",
                                "dataType": ["text"],
                            },
                            {
                                "name": "category",
                                "description": "Document category",
                                "dataType": ["text"],
                            },
                            {
                                "name": "chunk_id",
                                "description": "Chunk ID within document",
                                "dataType": ["int"],
                            },
                            {
                                "name": "document_path",
                                "description": "Path to source document",
                                "dataType": ["text"],
                            },
                        ],
                    }
                ]
            }
            
            self.client.schema.create(schema)
            self.logger.info(f"Created schema for class {self.class_name}")
            
        except Exception as e:
            self.logger.error(f"Error creating schema: {str(e)}")
            raise
    
    def add_embeddings(
        self,
        embeddings: List[List[float]],
        metadata: List[Dict[str, Any]]
    ) -> None:
        """
        Add embeddings to Weaviate.
        
        Args:
            embeddings (List[List[float]]): List of embedding vectors
            metadata (List[Dict]): Metadata for each embedding
        """
        if len(embeddings) == 0:
            self.logger.warning("No embeddings to add")
            return
        
        if len(embeddings) != len(metadata):
            raise ValueError("Embeddings and metadata lengths don't match")
        
        try:
            batch_size = 100
            added_count = 0
            
            for i in range(0, len(embeddings), batch_size):
                batch_embeddings = embeddings[i:i+batch_size]
                batch_metadata = metadata[i:i+batch_size]
                
                with self.client.batch as batch:
                    for embedding, meta in zip(batch_embeddings, batch_metadata):
                        # Prepare object
                        obj = {
                            "content": meta.get("content", ""),
                            "source": meta.get("source", ""),
                            "title": meta.get("title", ""),
                            "category": meta.get("category", ""),
                            "chunk_id": meta.get("chunk_id", 0),
                            "document_path": meta.get("document_path", ""),
                        }
                        
                        # Add to batch with vector
                        batch.add_data_object(
                            data_object=obj,
                            class_name=self.class_name,
                            vector=embedding
                        )
                
                added_count += len(batch_metadata)
                self.logger.info(f"Added {added_count}/{len(embeddings)} embeddings")
            
            self.logger.info(f"Successfully added {len(embeddings)} embeddings to Weaviate")
            
        except Exception as e:
            self.logger.error(f"Error adding embeddings: {str(e)}")
            raise
    
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar embeddings in Weaviate.
        
        Args:
            query_embedding (List[float]): Query embedding vector
            top_k (int): Number of results to return
            filters (Dict): Optional filters on metadata
            
        Returns:
            List[Dict]: Similar chunks with scores
        """
        if not self.client:
            self.logger.warning("Weaviate client not initialized")
            return []
        
        try:
            # Build where filter if provided
            where_filter = None
            if filters:
                where_filter = self._build_where_filter(filters)
            
            # Search using vector similarity
            response = (
                self.client.query
                .get(self.class_name, [
                    "content",
                    "source",
                    "title",
                    "category",
                    "chunk_id",
                    "document_path",
                    "_additional {distance}"
                ])
                .with_near_vector({
                    "vector": query_embedding
                })
                .with_where(where_filter)
                .with_limit(top_k)
                .do()
            )
            
            # Process results
            results = []
            if "data" in response and "Get" in response["data"]:
                objects = response["data"]["Get"].get(self.class_name, [])
                
                for obj in objects:
                    # Convert distance to similarity score
                    distance = obj.get("_additional", {}).get("distance", 0)
                    similarity_score = 1 - distance  # Cosine distance to similarity
                    
                    results.append({
                        "content": obj.get("content", ""),
                        "source": obj.get("source", ""),
                        "title": obj.get("title", ""),
                        "category": obj.get("category", ""),
                        "chunk_id": obj.get("chunk_id", 0),
                        "document_path": obj.get("document_path", ""),
                        "relevance_score": similarity_score,
                    })
            
            self.logger.info(f"Search returned {len(results)} results")
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching: {str(e)}")
            return []
    
    def _build_where_filter(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Build Weaviate where filter from metadata filters."""
        conditions = []
        
        for key, value in filters.items():
            conditions.append({
                "path": [key],
                "operator": "Equal",
                "valueString": str(value)
            })
        
        if len(conditions) == 1:
            return conditions[0]
        
        # Multiple conditions - use AND
        return {
            "operator": "And",
            "operands": conditions
        }
    
    def get_size(self) -> int:
        """Get number of objects in the store."""
        try:
            response = (
                self.client.query
                .aggregate(self.class_name)
                .with_meta_count()
                .do()
            )
            
            if "data" in response and "Aggregate" in response["data"]:
                count = response["data"]["Aggregate"][self.class_name][0].get("meta", {}).get("count", 0)
                return count
            return 0
            
        except Exception as e:
            self.logger.error(f"Error getting store size: {str(e)}")
            return 0
    
    def delete_all(self) -> None:
        """Delete all objects from the class."""
        try:
            self.client.schema.delete_class(self.class_name)
            self._create_schema()
            self.logger.info(f"Deleted and recreated class {self.class_name}")
        except Exception as e:
            self.logger.error(f"Error deleting all: {str(e)}")
            raise


# Legacy alias for backwards compatibility
VectorStore = WeaviateVectorStore
