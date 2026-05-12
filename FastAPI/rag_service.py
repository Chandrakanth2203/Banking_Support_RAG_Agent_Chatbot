"""
RAG (Retrieval-Augmented Generation) Service for Banking Support AI Agent Chatbot.
Orchestrates the complete RAG pipeline: ingestion, embedding, retrieval, and generation.

Located in: FastAPI/rag_service.py
Manages RAG components from: ../RAG/

Pipeline:
1. Document Ingestion: Load and chunk documents from Documents folder
2. Embedding: Generate embeddings for chunks using sentence transformers
3. Vector Indexing: Store embeddings in Weaviate vector database
4. Retrieval: Find relevant chunks using semantic similarity with re-ranking
5. Context Augmentation: Prepare context and prompts for LLM
6. Response Generation: Generate responses using LLM with RAG context
"""

import logging
import sys
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime

# Add RAG folder to path to import RAG components
rag_path = Path(__file__).parent.parent / "RAG"
if str(rag_path) not in sys.path:
    sys.path.insert(0, str(rag_path))

from document_ingestion import DocumentIngestion
from embedding import EmbeddingGenerator
from vector_store import WeaviateVectorStore
from retrieval import Retriever
from augmentation import ContextAugmentation
from generation import ResponseGenerator

logger = logging.getLogger(__name__)


class RAGService:
    """
    Complete RAG Service orchestrating all components in a clean pipeline.
    
    Pipeline flow:
    1. Initialize all components (embedding model, vector store, retriever, etc.)
    2. Load knowledge base (ingest documents, generate embeddings, index)
    3. Answer queries (retrieve → augment → generate)
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize RAG service.
        
        Args:
            config (Dict): Configuration dictionary with settings
        """
        self.config = config or self._get_default_config()
        self.logger = logger
        
        # Initialize pipeline components
        self.ingestion = DocumentIngestion(
            chunk_size=self.config.get("chunk_size", 512),
            overlap=self.config.get("overlap", 50),
        )
        
        # These will be initialized in initialize()
        self.embeddings: Optional[EmbeddingGenerator] = None
        self.vector_store: Optional[WeaviateVectorStore] = None
        self.retriever: Optional[Retriever] = None
        self.augmentation = ContextAugmentation(
            max_context_tokens=self.config.get("max_context_tokens", 2000)
        )
        self.generator = ResponseGenerator(
            model_name=self.config.get("model_name", "gpt-4")
        )
        
        # State tracking
        self.documents: List[Dict[str, Any]] = []
        self.initialized = False
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for RAG pipeline."""
        return {
            "chunk_size": 512,
            "overlap": 50,
            "embedding_model": "all-MiniLM-L6-v2",
            "max_context_tokens": 2000,
            "model_name": "gpt-4",
            "top_k": 5,
            "weaviate_url": "http://localhost:8080",
            "weaviate_api_key": None,
            "use_reranker": True,
        }
    
    async def initialize(self) -> None:
        """
        Initialize the RAG service with all pipeline components.
        Initializes embedding model, vector store, retriever, and loads knowledge base.
        """
        try:
            self.logger.info("=" * 80)
            self.logger.info("INITIALIZING RAG SERVICE")
            self.logger.info("=" * 80)
            
            # Step 1: Initialize embedding model
            self._initialize_embeddings()
            
            # Step 2: Initialize vector store
            self._initialize_vector_store()
            
            # Step 3: Initialize retriever
            self._initialize_retriever()
            
            # Step 4: Load and index knowledge base
            await self._load_knowledge_base()
            
            self.initialized = True
            self.logger.info("=" * 80)
            self.logger.info("✓ RAG SERVICE INITIALIZED SUCCESSFULLY")
            self.logger.info("=" * 80)
            
        except Exception as e:
            self.logger.error(f"✗ Error initializing RAG Service: {str(e)}")
            raise
    
    def _initialize_embeddings(self) -> None:
        """Initialize embedding generator component."""
        try:
            self.logger.info("\n[1/4] Initializing Embedding Model...")
            self.logger.info(f"   Model: {self.config['embedding_model']}")
            
            self.embeddings = EmbeddingGenerator(
                model_name=self.config["embedding_model"]
            )
            
            self.logger.info(f"   ✓ Embedding dimension: {self.embeddings.embedding_dim}")
        except Exception as e:
            self.logger.error(f"   ✗ Failed to initialize embeddings: {str(e)}")
            raise
    
    def _initialize_vector_store(self) -> None:
        """Initialize Weaviate vector store component."""
        try:
            self.logger.info("\n[2/4] Initializing Weaviate Vector Store...")
            self.logger.info(f"   URL: {self.config['weaviate_url']}")
            
            embedding_dim = self.embeddings.embedding_dim
            
            self.vector_store = WeaviateVectorStore(
                url=self.config.get("weaviate_url", "http://localhost:8080"),
                api_key=self.config.get("weaviate_api_key"),
                embedding_dim=embedding_dim,
                class_name="DocumentChunk"
            )
            
            self.logger.info("   ✓ Vector store connected and schema created")
        except Exception as e:
            self.logger.error(f"   ✗ Failed to initialize vector store: {str(e)}")
            raise
    
    def _initialize_retriever(self) -> None:
        """Initialize retriever component with embedding generator and vector store."""
        try:
            self.logger.info("\n[3/4] Initializing Retriever...")
            self.logger.info(f"   Re-ranker enabled: {self.config.get('use_reranker', True)}")
            
            self.retriever = Retriever(
                embedding_generator=self.embeddings,
                vector_store=self.vector_store,
                use_reranker=self.config.get("use_reranker", True)
            )
            
            self.logger.info("   ✓ Retriever initialized with embedding and vector store")
        except Exception as e:
            self.logger.error(f"   ✗ Failed to initialize retriever: {str(e)}")
            raise
    
    async def _load_knowledge_base(self) -> None:
        """
        Load knowledge base: ingest documents → generate embeddings → index.
        
        This is the final initialization step that populates the vector store.
        """
        try:
            self.logger.info("\n[4/4] Loading Knowledge Base...")
            
            # Step 4a: Ingest documents from Documents folder
            # Documents folder is at root level: ../Documents
            documents_folder = Path(__file__).parent.parent / "Documents"
            self.logger.info(f"   Ingesting documents from: {documents_folder}")
            
            documents = self.ingestion.ingest_documents(documents_folder)
            self.documents = documents
            
            if not documents:
                self.logger.warning("   ⚠ No documents found in Documents folder")
                return
            
            self.logger.info(f"   ✓ Ingested {len(documents)} documents")
            
            # Step 4b: Extract and prepare chunks for embedding
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
            
            self.logger.info(f"   ✓ Prepared {len(all_chunks)} chunks for embedding")
            
            # Step 4c: Generate embeddings using embedding component
            self.logger.info("   Generating embeddings...")
            embeddings = self.embeddings.generate_embeddings(all_chunks)
            self.logger.info(f"   ✓ Generated embeddings with shape: {embeddings.shape}")
            
            # Step 4d: Index embeddings in vector store
            self.logger.info("   Indexing embeddings in Weaviate...")
            self.vector_store.add_embeddings(embeddings, all_metadata)
            self.logger.info(f"   ✓ Indexed {len(all_chunks)} embeddings")
            
            # Summary
            stats = self.vector_store.get_size()
            self.logger.info(f"\n   Knowledge Base Summary:")
            self.logger.info(f"   - Documents: {len(documents)}")
            self.logger.info(f"   - Total chunks: {len(all_chunks)}")
            self.logger.info(f"   - Indexed embeddings: {stats}")
            
        except Exception as e:
            self.logger.error(f"   ✗ Error loading knowledge base: {str(e)}")
            raise
    
    async def search_knowledge_base(
        self,
        query: str,
        top_k: Optional[int] = None,
        category_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search knowledge base for relevant documents using semantic similarity.
        
        Uses the Retriever component which:
        1. Preprocesses the query
        2. Generates query embedding
        3. Searches vector store
        4. Re-ranks results (if enabled)
        
        Args:
            query (str): User query
            top_k (int): Number of results to return
            category_filter (str): Filter by document category
            
        Returns:
            List[Dict]: Relevant document chunks ranked by relevance
        """
        if not self.initialized:
            self.logger.warning("RAG Service not initialized")
            return []
        
        try:
            top_k = top_k or self.config["top_k"]
            
            self.logger.info(f"Searching knowledge base: '{query}' (top_k={top_k})")
            
            # Use retriever component to retrieve and re-rank results
            results = self.retriever.retrieve(
                query=query,
                top_k=top_k,
                category_filter=category_filter,
            )
            
            self.logger.info(f"Retrieved {len(results)} results")
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching knowledge base: {str(e)}")
            return []
    
    async def generate_response(
        self,
        query: str,
        top_k: Optional[int] = None,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """
        Generate a response using the complete RAG pipeline: Retrieve → Augment → Generate
        
        Pipeline:
        1. Retrieve: Use retriever to find relevant documents
        2. Augment: Use context augmentation to assemble context and create prompt
        3. Generate: Use response generator to generate LLM response
        
        Args:
            query (str): User query
            top_k (int): Number of context chunks to retrieve
            temperature (float): LLM temperature (0.0-1.0)
            
        Returns:
            Dict: Response with content, sources, and metadata
        """
        try:
            self.logger.info(f"\n{'='*80}")
            self.logger.info(f"GENERATING RESPONSE FOR QUERY: {query}")
            self.logger.info(f"{'='*80}")
            
            # Step 1: RETRIEVE - Search knowledge base using retriever component
            self.logger.info("\n[Step 1] RETRIEVAL")
            retrieved_chunks = await self.search_knowledge_base(query, top_k)
            self.logger.info(f"   ✓ Retrieved {len(retrieved_chunks)} relevant chunks")
            
            # Step 2: AUGMENT - Assemble context using augmentation component
            self.logger.info("\n[Step 2] AUGMENTATION")
            context = self.augmentation.assemble_context(retrieved_chunks)
            prompt = self.augmentation.create_prompt(query, context)
            self.logger.info(f"   ✓ Created prompt ({len(prompt)} characters)")
            
            # Step 3: GENERATE - Generate response using generation component
            self.logger.info("\n[Step 3] GENERATION")
            response = self.generator.generate(
                prompt=prompt,
                temperature=temperature,
                max_tokens=512,
            )
            self.logger.info(f"   ✓ Generated response ({response['tokens_used']['total']} tokens)")
            
            # Format final response with sources
            formatted_response = {
                "response": response.get("content", ""),
                "query": query,
                "sources": [
                    {
                        "title": chunk.get("title"),
                        "source": chunk.get("source"),
                        "relevance": chunk.get("relevance_score", 0),
                    }
                    for chunk in retrieved_chunks
                ],
                "model": response.get("model"),
                "tokens_used": response.get("tokens_used"),
                "timestamp": datetime.now().isoformat(),
                "success": response.get("success", False),
            }
            
            self.logger.info(f"\n{'='*80}")
            self.logger.info("✓ RESPONSE GENERATED SUCCESSFULLY")
            self.logger.info(f"{'='*80}\n")
            
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
        Add a new document to the knowledge base dynamically.
        
        Uses the ingestion and embedding components to process and index the document.
        
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
            
            self.logger.info(f"Adding new document: '{title}'")
            
            # Step 1: Clean and chunk content using ingestion component
            cleaned = self.ingestion._clean_text(content)
            chunks = self.ingestion._chunk_text(cleaned)
            
            self.logger.info(f"   ✓ Created {len(chunks)} chunks")
            
            # Step 2: Generate embeddings using embedding component
            chunk_contents = [c["content"] for c in chunks]
            embeddings = self.embeddings.generate_embeddings(chunk_contents)
            
            self.logger.info(f"   ✓ Generated embeddings")
            
            # Step 3: Prepare metadata
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
            
            # Step 4: Index in vector store
            self.vector_store.add_embeddings(embeddings, metadata)
            
            doc_id = f"doc_{len(self.documents) + 1}"
            self.logger.info(f"   ✓ Document added with ID: {doc_id}")
            
            return doc_id
            
        except Exception as e:
            self.logger.error(f"Error adding document: {str(e)}")
            raise
    
    async def get_document_count(self) -> int:
        """Get total number of loaded documents."""
        return len(self.documents)
    
    async def get_knowledge_base_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive knowledge base statistics.
        
        Returns:
            Dict: Statistics including document count, chunks, categories, etc.
        """
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
            "vector_store_url": self.config["weaviate_url"],
            "initialized": self.initialized,
        }
