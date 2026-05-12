"""
RAG (Retrieval-Augmented Generation) Module for Banking Support AI Agent Chatbot.

Complete RAG pipeline implementation with:
- Document Ingestion: Load and chunk documents from various formats
- Embedding Generation: Convert text to vectors using pre-trained models
- Vector Storage: Store and retrieve embeddings using Weaviate vector database
- Semantic Retrieval: Find relevant documents using vector similarity with re-ranking
- Context Augmentation: Prepare context for LLM
- Response Generation: Generate grounded responses with citations

Pipeline:
1. DocumentIngestion -> chunks documents into manageable pieces
2. EmbeddingGenerator -> converts chunks to vectors
3. WeaviateVectorStore -> stores and indexes vectors with schema management
4. Retriever -> searches with vector similarity and cross-encoder re-ranking
5. ContextAugmentation -> assembles context and prompts
6. ResponseGenerator -> generates LLM responses
7. RAGService -> orchestrates entire pipeline (located in FastAPI folder)

Example:
    >>> from RAG import RAGService
    >>> rag_svc = RAGService()
    >>> await rag_svc.initialize()
    >>> response = await rag_svc.generate_response("How do I open an account?")
    >>> print(response["response"])
"""

# Import RAGService from FastAPI folder where service orchestration is centralized
import sys
from pathlib import Path

root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

try:
    from FastAPI.rag_service import RAGService
except ImportError:
    raise ImportError("RAGService not found in FastAPI folder")

# Import all RAG components from this folder
from .document_ingestion import DocumentIngestion
from .embedding import EmbeddingGenerator
from .vector_store import WeaviateVectorStore, VectorStore
from .retrieval import Retriever
from .augmentation import ContextAugmentation
from .generation import ResponseGenerator
from .llm_agent import LLMAgent, ShortTermMemory, CalculatorTools

__all__ = [
    "RAGService",
    "DocumentIngestion",
    "EmbeddingGenerator",
    "WeaviateVectorStore",
    "VectorStore",
    "Retriever",
    "ContextAugmentation",
    "ResponseGenerator",
    "LLMAgent",
    "ShortTermMemory",
    "CalculatorTools",
]

__version__ = "2.0.0"
__author__ = "Banking Support Team"
__description__ = "RAG Service with Weaviate and Re-ranking for Banking Support AI Agent Chatbot"
