"""
Document Ingestion Module for RAG System.
Handles document loading, parsing, cleaning, and chunking.
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import re

logger = logging.getLogger(__name__)


class DocumentIngestion:
    """Handles document ingestion, parsing, and preprocessing."""
    
    def __init__(self, chunk_size: int = 512, overlap: int = 50):
        """
        Initialize document ingestion.
        
        Args:
            chunk_size (int): Size of chunks in characters (~tokens)
            overlap (int): Overlap between chunks in characters
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.logger = logger
    
    def ingest_documents(self, documents_folder: Path) -> List[Dict[str, Any]]:
        """
        Ingest all documents from a folder.
        
        Args:
            documents_folder (Path): Path to documents folder
            
        Returns:
            List[Dict]: List of processed documents with chunks
        """
        processed_docs = []
        
        if not documents_folder.exists():
            self.logger.warning(f"Documents folder not found: {documents_folder}")
            return []
        
        for file_path in documents_folder.glob("*"):
            if not file_path.is_file():
                continue
            
            try:
                self.logger.info(f"Ingesting document: {file_path.name}")
                
                # Extract text based on file type
                if file_path.suffix.lower() == '.docx':
                    text = self._extract_docx(str(file_path))
                elif file_path.suffix.lower() in ['.txt', '.md']:
                    text = self._extract_text(str(file_path))
                else:
                    text = self._extract_text(str(file_path))
                
                if not text:
                    self.logger.warning(f"No text extracted from {file_path.name}")
                    continue
                
                # Clean text
                text = self._clean_text(text)
                
                # Create chunks
                chunks = self._chunk_text(text)
                
                # Create document object
                doc = {
                    "source": file_path.name,
                    "source_path": str(file_path),
                    "title": file_path.stem,
                    "category": self._categorize(file_path.stem),
                    "full_text": text,
                    "chunks": chunks,
                    "metadata": {
                        "file_type": file_path.suffix,
                        "file_size": file_path.stat().st_size,
                        "num_chunks": len(chunks),
                    }
                }
                
                processed_docs.append(doc)
                self.logger.info(f"Successfully ingested {file_path.name} with {len(chunks)} chunks")
                
            except Exception as e:
                self.logger.error(f"Error ingesting {file_path.name}: {str(e)}")
                continue
        
        self.logger.info(f"Ingestion complete: {len(processed_docs)} documents processed")
        return processed_docs
    
    def _extract_docx(self, file_path: str) -> str:
        """Extract text from .docx file."""
        try:
            from docx import Document
            doc = Document(file_path)
            paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
            return "\n".join(paragraphs)
        except ImportError:
            self.logger.warning("python-docx not installed. Install with: pip install python-docx")
            return ""
        except Exception as e:
            self.logger.error(f"Error extracting .docx: {str(e)}")
            return ""
    
    def _extract_text(self, file_path: str) -> str:
        """Extract text from text file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            self.logger.error(f"Error extracting text: {str(e)}")
            return ""
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text.
        
        Args:
            text (str): Raw text
            
        Returns:
            str: Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', text)
        
        # Remove multiple spaces
        text = re.sub(r' +', ' ', text)
        
        # Trim
        text = text.strip()
        
        return text
    
    def _chunk_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Split text into chunks with overlap.
        
        Args:
            text (str): Text to chunk
            
        Returns:
            List[Dict]: List of chunks with position info
        """
        chunks = []
        start = 0
        chunk_id = 0
        
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for period, question mark, or exclamation mark
                break_point = max(
                    text.rfind('.', start, end),
                    text.rfind('!', start, end),
                    text.rfind('?', start, end),
                )
                
                if break_point > start + self.chunk_size // 2:
                    end = break_point + 1
            
            chunk_text = text[start:end].strip()
            
            if len(chunk_text) > 50:  # Only include chunks with meaningful content
                chunks.append({
                    "chunk_id": chunk_id,
                    "content": chunk_text,
                    "start": start,
                    "end": end,
                    "length": len(chunk_text),
                })
                chunk_id += 1
            
            # Move start position (with overlap)
            start = end - self.overlap
        
        return chunks
    
    def _categorize(self, title: str) -> str:
        """Categorize document based on title."""
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
