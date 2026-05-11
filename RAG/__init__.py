"""
RAG (Retrieval-Augmented Generation) Module for Banking Support AI Agent Chatbot.

Complete RAG pipeline implementation with:
- Document Ingestion: Load and chunk documents from various formats
- Embedding Generation: Convert text to vectors using pre-trained models
- Vector Storage: Store and retrieve embeddings using FAISS
- Semantic Retrieval: Find relevant documents using vector similarity
- Context Augmentation: Prepare context for LLM
- Response Generation: Generate grounded responses with citations

Pipeline:
1. DocumentIngestion -> chunks documents into manageable pieces
2. EmbeddingGenerator -> converts chunks to vectors
3. VectorStore (FAISS) -> stores and indexes vectors
4. Retriever -> searches for relevant chunks
5. ContextAugmentation -> assembles context and prompts
6. ResponseGenerator -> generates LLM responses
7. RAGService -> orchestrates entire pipeline

Example:
    >>> from RAG import RAGService
    >>> rag_svc = RAGService()
    >>> await rag_svc.initialize()
    >>> response = await rag_svc.generate_response("How do I open an account?")
    >>> print(response["response"])
"""

from .rag_service import RAGService
from .document_ingestion import DocumentIngestion
from .embedding import EmbeddingGenerator
from .vector_store import VectorStore
from .retrieval import Retriever
from .augmentation import ContextAugmentation
from .generation import ResponseGenerator

__all__ = [
    "RAGService",
    "DocumentIngestion",
    "EmbeddingGenerator",
    "VectorStore",
    "Retriever",
    "ContextAugmentation",
    "ResponseGenerator",
]

__version__ = "1.0.0"
__author__ = "Banking Support Team"
__description__ = "RAG Service with Complete Pipeline for Banking Support AI Agent Chatbot"
