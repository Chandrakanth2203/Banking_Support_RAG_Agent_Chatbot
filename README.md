# Support_Resolution_Multi_Agent_AG_Chatbot

Streamlit (Frontend)
    ↓
API Client (HTTP Calls)
    ↓
FastAPI/main.py
    ↓
services/__init__.py (imports from RAG folder)
    ↓
RAG/rag_service.py (Handles knowledge base operations)
    ↓
Documents/ (Knowledge base files)