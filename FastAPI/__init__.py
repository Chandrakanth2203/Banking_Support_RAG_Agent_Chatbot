"""
Banking Support AI Agent Chatbot - FastAPI Backend

A comprehensive FastAPI backend providing:
- RESTful APIs for chat processing
- RAG (Retrieval-Augmented Generation) integration
- Multi-agent routing system
- User feedback collection and analysis
- Knowledge base management
- System monitoring and health checks

Modules:
    main: FastAPI application and route definitions
    config: Configuration settings
    models: Pydantic request/response schemas
    services: Business logic services

Usage:
    >>> from fastapi import FastAPI
    >>> app = FastAPI()
    >>> # Server runs on http://localhost:8000
    >>> # API docs available at http://localhost:8000/docs

Documentation:
    - API Docs: http://localhost:8000/docs
    - ReDoc: http://localhost:8000/redoc
    - README: See FastAPI/README.md

"""

__version__ = "1.0.0"
__author__ = "Banking Support Team"
__title__ = "Banking Support AI Agent Chatbot API"
__description__ = "FastAPI backend for multi-agent banking support chatbot"
__license__ = "MIT"

# Version info
VERSION_INFO = (1, 0, 0)
