"""
RAG (Retrieval-Augmented Generation) Service for Banking Support AI Agent Chatbot.
Handles knowledge base search and document management.
"""

import logging
from typing import Dict, List, Optional, Any
import json
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class RAGService:
    """Service for RAG-based knowledge base search."""
    
    def __init__(self):
        """Initialize the RAG service."""
        self.documents: Dict[str, Dict[str, Any]] = {}
        self.document_counter = 0
        self.logger = logger
    
    async def initialize(self):
        """Initialize the service."""
        self.logger.info("RAGService initialized")
        # In production, load knowledge base from database/vector store
        await self._load_sample_knowledge_base()
    
    async def _load_sample_knowledge_base(self):
        """Load knowledge base from Documents folder."""
        try:
            # Get the Documents folder path
            # Navigate from RAG folder up to Support_Resolution... folder
            base_path = Path(__file__).parent.parent
            docs_folder = base_path / "Documents"
            
            if not docs_folder.exists():
                self.logger.warning(f"Documents folder not found at {docs_folder}")
                return
            
            # Load all documents from the Documents folder
            for file_path in docs_folder.glob("*"):
                if file_path.is_file():
                    try:
                        # Extract title from filename (without extension)
                        title = file_path.stem
                        
                        # Read file content
                        if file_path.suffix.lower() == '.docx':
                            # For .docx files, try to extract text
                            content = self._extract_docx_content(str(file_path))
                        elif file_path.suffix.lower() in ['.txt', '.md']:
                            # For text files
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                        else:
                            # Try to read as text for other formats
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                        
                        # Determine category based on filename
                        category = self._categorize_document(title)
                        
                        # Add document to knowledge base
                        await self.add_document(
                            title=title,
                            content=content,
                            category=category,
                        )
                        
                    except Exception as e:
                        self.logger.error(f"Error loading document {file_path}: {str(e)}")
                        continue
            
            self.logger.info(f"Loaded {len(self.documents)} documents from {docs_folder}")
            
        except Exception as e:
            self.logger.error(f"Error loading knowledge base from Documents folder: {str(e)}")
    
    def _extract_docx_content(self, file_path: str) -> str:
        """Extract text content from a .docx file."""
        try:
            from docx import Document
            doc = Document(file_path)
            content = "\n".join([para.text for para in doc.paragraphs])
            return content if content.strip() else "Document content could not be extracted."
        except ImportError:
            # If python-docx is not installed, return a placeholder
            self.logger.warning("python-docx not installed. Cannot extract .docx content.")
            return "Document requires python-docx library for content extraction."
        except Exception as e:
            self.logger.error(f"Error extracting .docx content: {str(e)}")
            return "Error extracting document content."
    
    def _categorize_document(self, title: str) -> str:
        """Categorize document based on its title."""
        title_lower = title.lower()
        
        if 'faq' in title_lower or 'question' in title_lower:
            return "FAQs"
        elif 'policy' in title_lower or 'manual' in title_lower:
            return "Policies"
        elif 'product' in title_lower or 'brochure' in title_lower:
            return "Products"
        elif 'regulatory' in title_lower or 'rbi' in title_lower or 'guidelines' in title_lower:
            return "Regulatory"
        else:
            return "General"
    
    async def add_document(
        self,
        title: str,
        content: str,
        category: Optional[str] = None,
    ) -> str:
        """Add a document to the knowledge base."""
        self.document_counter += 1
        doc_id = f"doc_{self.document_counter}"
        
        self.documents[doc_id] = {
            "document_id": doc_id,
            "title": title,
            "content": content,
            "category": category,
        }
        
        self.logger.info(f"Added document to knowledge base: {title}")
        return doc_id
    
    async def search_knowledge_base(
        self,
        query: str,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """Search knowledge base for relevant documents."""
        # Simple keyword matching (in production, use vector similarity with embeddings)
        results = []
        query_lower = query.lower()
        
        for doc_id, doc in self.documents.items():
            # Simple keyword matching score
            score = 0.0
            
            # Check title
            if query_lower in doc["title"].lower():
                score += 0.5
            
            # Check content
            content_lower = doc["content"].lower()
            words = query_lower.split()
            for word in words:
                if word in content_lower:
                    score += 0.1
            
            if score > 0:
                results.append({
                    "document_id": doc_id,
                    "title": doc["title"],
                    "content": doc["content"],
                    "category": doc.get("category"),
                    "relevance_score": min(score, 1.0),
                })
        
        # Sort by relevance and return top_k
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        self.logger.info(f"Knowledge base search for '{query}' returned {len(results)} results")
        
        return results[:top_k]
    
    async def get_document_count(self) -> int:
        """Get total number of documents in knowledge base."""
        return len(self.documents)
    
    async def get_knowledge_base_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics."""
        categories = {}
        for doc in self.documents.values():
            category = doc.get("category", "Uncategorized")
            categories[category] = categories.get(category, 0) + 1
        
        return {
            "total_documents": len(self.documents),
            "categories": categories,
            "last_updated": "2024-05-10",  # In production, track actual updates
        }
