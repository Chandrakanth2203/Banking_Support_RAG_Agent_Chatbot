"""
RAG (Retrieval-Augmented Generation) Service for Banking Support AI Agent Chatbot.
Orchestrates the complete RAG pipeline: ingestion, embedding, retrieval, and generation.

Pipeline:
1. Document Ingestion: Load and chunk documents
2. Embedding: Generate embeddings for chunks using sentence transformers
3. Indexing: Store embeddings in FAISS vector database
4. Retrieval: Find relevant chunks using semantic similarity
5. Augmentation: Prepare context and prompts for LLM
6. Generation: Generate responses using LLM with RAG context
"""

import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime

from .document_ingestion import DocumentIngestion
from .embedding import EmbeddingGenerator
from .vector_store import WeaviateVectorStore
from .retrieval import Retriever
from .augmentation import ContextAugmentation
from .generation import ResponseGenerator

logger = logging.getLogger(__name__)


class RAGService:
    """
    Complete RAG Service orchestrating all components.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize RAG service.
        
        Args:
            config (Dict): Configuration dictionary with settings
        """
        self.config = config or self._get_default_config()
        self.logger = logger
        
        # Components
        self.ingestion = DocumentIngestion(
            chunk_size=self.config.get("chunk_size", 512),
            overlap=self.config.get("overlap", 50),
        )
        
        self.embeddings = None
        self.vector_store = None
        self.retriever = None
        self.augmentation = ContextAugmentation(
            max_context_tokens=self.config.get("max_context_tokens", 2000)
        )
        self.generator = ResponseGenerator(
            model_name=self.config.get("model_name", "gpt-4")
        )
        
        # State
        self.documents = []
        self.initialized = False
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "chunk_size": 512,
            "overlap": 50,
            "embedding_model": "all-MiniLM-L6-v2",
            "max_context_tokens": 2000,
            "model_name": "gpt-4",
            "top_k": 5,
            "weaviate_url": "http://localhost:8080",
            "weaviate_api_key": None,
        }
    
    async def initialize(self) -> None:
        """Initialize the RAG service with all components."""
        try:
            self.logger.info("Initializing RAG Service...")
            
            # Initialize embedding generator
            self.logger.info(f"Loading embedding model: {self.config['embedding_model']}")
            self.embeddings = EmbeddingGenerator(
                model_name=self.config["embedding_model"]
            )
            
            # Initialize Weaviate vector store
            embedding_dim = self.embeddings.get_embedding_dimension()
            self.logger.info(f"Initializing Weaviate vector store at {self.config['weaviate_url']}")
            self.vector_store = WeaviateVectorStore(
                url=self.config.get("weaviate_url", "http://localhost:8080"),
                api_key=self.config.get("weaviate_api_key"),
                embedding_dim=embedding_dim,
                class_name="DocumentChunk"
            )
            
            # Initialize retriever with re-ranking enabled
            self.retriever = Retriever(
                self.embeddings,
                self.vector_store,
                use_reranker=self.config.get("use_reranker", True)
            )
            
            # Load documents
            await self._load_knowledge_base()
            
            self.initialized = True
            self.logger.info("RAG Service initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing RAG Service: {str(e)}")
            raise
    
    async def _load_knowledge_base(self) -> None:
        """Load and process documents from Documents folder."""
        try:
            documents_folder = Path(__file__).parent.parent / "Documents"
            
            if not documents_folder.exists():
                self.logger.warning(f"Documents folder not found: {documents_folder}")
                return
            
            self.logger.info(f"Loading documents from: {documents_folder}")
            
            # Ingest documents
            documents = self.ingestion.ingest_documents(documents_folder)
            self.documents = documents
            
            if not documents:
                self.logger.warning("No documents ingested")
                return
            
            # Extract all chunks and generate embeddings
            all_chunks = []
            all_metadata = []
            
            for doc in documents:
                for chunk in doc["chunks"]:
                    all_chunks.append(chunk["content"])
                    all_metadata.append({
                        "content": chunk["content"],
                        "source": doc["source"],
                        "title": doc["title"],
                        "category": doc["category"],
                        "chunk_id": chunk["chunk_id"],
                        "document_path": doc["source_path"],
                    })
            
            self.logger.info(f"Processing {len(all_chunks)} chunks for embedding...")
            
            # Generate embeddings
            embeddings = self.embeddings.generate_embeddings(all_chunks)
            
            # Add to vector store
            self.vector_store.add_embeddings(embeddings, all_metadata)
            
            self.logger.info(f"Knowledge base loaded: {len(documents)} documents, "
                           f"{len(all_chunks)} chunks, "
                           f"{self.vector_store.get_size()} embeddings in index")
            
        except Exception as e:
            self.logger.error(f"Error loading knowledge base: {str(e)}")
            raise
    
    async def search_knowledge_base(
        self,
        query: str,
        top_k: Optional[int] = None,
        category_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search knowledge base for relevant documents using semantic similarity.
        
        Args:
            query (str): User query
            top_k (int): Number of results to return
            category_filter (str): Filter by category
            
        Returns:
            List[Dict]: Relevant document chunks with scores
        """
        if not self.initialized:
            self.logger.warning("RAG Service not initialized")
            return []
        
        try:
            top_k = top_k or self.config["top_k"]
            
            results = self.retriever.retrieve(
                query=query,
                top_k=top_k,
                category_filter=category_filter,
            )
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching: {str(e)}")
            return []
    
    async def generate_response(
        self,
        query: str,
        top_k: Optional[int] = None,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """
        Generate a response using the complete RAG pipeline.
        
        Args:
            query (str): User query
            top_k (int): Number of context chunks
            temperature (float): LLM temperature
            
        Returns:
            Dict: Response with sources and metadata
        """
        try:
            # 1. Retrieve
            retrieved_chunks = await self.search_knowledge_base(query, top_k)
            
            # 2. Augment
            context = self.augmentation.assemble_context(retrieved_chunks)
            prompt = self.augmentation.create_prompt(query, context)
            
            # 3. Generate
            response = self.generator.generate(
                prompt=prompt,
                temperature=temperature,
                max_tokens=512,
            )
            
            # 4. Format
            formatted_response = {
                "response": response.get("content", ""),
                "query": query,
                "sources": [
                    {
                        "title": chunk["title"],
                        "source": chunk["source"],
                        "relevance": chunk["relevance_score"],
                    }
                    for chunk in retrieved_chunks
                ],
                "model": response.get("model"),
                "tokens_used": response.get("tokens_used"),
                "timestamp": datetime.now().isoformat(),
                "success": response.get("success", False),
            }
            
            return formatted_response
            
        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
            return {
                "response": f"Error: {str(e)}",
                "query": query,
                "sources": [],
                "success": False,
                "error": str(e),
            }
    
    async def add_document(
        self,
        title: str,
        content: str,
        category: Optional[str] = None,
    ) -> str:
        """
        Add a new document to the knowledge base.
        
        Args:
            title (str): Document title
            content (str): Document content
            category (str): Document category
            
        Returns:
            str: Document ID
        """
        try:
            if not self.initialized:
                raise ValueError("RAG Service not initialized")
            
            # Create document entry
            doc_id = f"doc_{len(self.documents) + 1}"
            
            # Clean and chunk content
            cleaned = self.ingestion._clean_text(content)
            chunks = self.ingestion._chunk_text(cleaned)
            
            # Generate embeddings
            chunk_contents = [c["content"] for c in chunks]
            embeddings = self.embeddings.generate_embeddings(chunk_contents)
            
            # Create metadata
            metadata = []
            for chunk in chunks:
                metadata.append({
                    "content": chunk["content"],
                    "source": title,
                    "title": title,
                    "category": category or "General",
                    "chunk_id": chunk["chunk_id"],
                    "document_path": "",
                })
            
            # Add to vector store
            self.vector_store.add_embeddings(embeddings, metadata)
            
            self.logger.info(f"Added document: {title} with {len(chunks)} chunks")
            return doc_id
            
        except Exception as e:
            self.logger.error(f"Error adding document: {str(e)}")
            raise
    
    async def get_document_count(self) -> int:
        """Get total number of documents."""
        return len(self.documents)
    
    async def get_knowledge_base_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics."""
        categories = {}
        total_chunks = 0
        
        for doc in self.documents:
            category = doc.get("category", "Uncategorized")
            categories[category] = categories.get(category, 0) + len(doc["chunks"])
            total_chunks += len(doc["chunks"])
        
        return {
            "total_documents": len(self.documents),
            "total_chunks": total_chunks,
            "embeddings_in_index": self.vector_store.get_size() if self.vector_store else 0,
            "categories": categories,
            "embedding_model": self.config["embedding_model"],
            "initialized": self.initialized,
        }
