"""
RAG (Retrieval-Augmented Generation) Module for Banking Support AI Agent Chatbot.

This module contains all RAG-related functionality for knowledge base management
and document retrieval using simple keyword matching (with future support for
vector embeddings and semantic search).

Modules:
    rag_service: RAGService for knowledge base operations

Classes:
    RAGService: Handles knowledge base search and document management

Features:
    - Load documents from Documents folder (supports .docx, .txt, .md)
    - Keyword-based search with relevance scoring
    - Document categorization and management
    - Knowledge base statistics and monitoring
    - Future: Vector embeddings and semantic search

Example:
    >>> from RAG import RAGService
    >>> rag_svc = RAGService()
    >>> await rag_svc.initialize()
    >>> results = await rag_svc.search_knowledge_base("password reset")
    >>> stats = await rag_svc.get_knowledge_base_stats()
"""

from .rag_service import RAGService

__all__ = ["RAGService"]

__version__ = "1.0.0"
__author__ = "Banking Support Team"
__description__ = "RAG Service for Banking Support AI Agent Chatbot"
