"""Document ingestion service: parsing, splitting, and embedding."""

import uuid
from typing import List, Optional, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rag.types import Document, Chunk
from rag.config import settings
from rag.llm.ollama_wrapper import OllamaEmbeddings


class DocumentIngestionService:
    """Service for parsing, chunking, and embedding documents."""
    
    def __init__(self):
        """Initialize ingestion service."""
        self.embeddings = OllamaEmbeddings()
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
    
    def parse_file(
        self,
        content: str,
        filename: str,
        doc_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Document:
        """
        Parse file content into a Document.
        
        Args:
            content: Raw text content
            filename: Source filename
            doc_id: Optional document ID (generated if not provided)
            metadata: Optional metadata dict
            
        Returns:
            Document object
        """
        if doc_id is None:
            doc_id = str(uuid.uuid4())
        
        # Extract title (first line or from filename)
        lines = content.strip().split('\n')
        title = lines[0][:100] if lines else filename
        
        return Document(
            id=doc_id,
            title=title,
            content=content,
            tags=metadata.get('tags', []) if metadata else [],
            source=metadata.get('source', filename) if metadata else filename,
            metadata=metadata or {}
        )
    
    def split_text(self, document: Document) -> List[Chunk]:
        """
        Split document into chunks.
        
        Args:
            document: Document to split
            
        Returns:
            List of Chunk objects
        """
        # Combine title and content for splitting
        full_text = f"{document.title}\n\n{document.content}"
        
        # Split using LangChain text splitter
        text_chunks = self.splitter.split_text(full_text)
        
        chunks = []
        for idx, chunk_text in enumerate(text_chunks):
            chunk = Chunk(
                id=f"{document.id}_chunk_{idx}",
                doc_id=document.id,
                content=chunk_text,
                chunk_index=idx,
                filename=document.source or f"{document.id}.txt",
                metadata={
                    "title": document.title,
                    "tags": document.tags,
                    **document.metadata
                }
            )
            chunks.append(chunk)
        
        return chunks
    
    def embed_chunks(self, chunks: List[Chunk]) -> List[List[float]]:
        """
        Generate embeddings for chunks.
        
        Args:
            chunks: List of chunks to embed
            
        Returns:
            List of embedding vectors
        """
        texts = [chunk.content for chunk in chunks]
        return self.embeddings.embed_documents(texts)
    
    def process_document(
        self,
        content: str,
        filename: str,
        doc_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> tuple[Document, List[Chunk], List[List[float]]]:
        """
        Full pipeline: parse -> split -> embed.
        
        Args:
            content: Raw text content
            filename: Source filename
            doc_id: Optional document ID
            metadata: Optional metadata
            
        Returns:
            Tuple of (document, chunks, embeddings)
        """
        document = self.parse_file(content, filename, doc_id, metadata)
        chunks = self.split_text(document)
        embeddings = self.embed_chunks(chunks)
        
        return document, chunks, embeddings


