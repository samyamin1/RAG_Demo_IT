"""Type definitions for the RAG module."""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class Document(BaseModel):
    """Represents a source document."""
    id: str
    title: str
    content: str
    tags: Optional[List[str]] = []
    source: Optional[str] = None
    metadata: Optional[dict] = {}


class Chunk(BaseModel):
    """Represents a text chunk from a document."""
    id: str
    doc_id: str
    content: str
    chunk_index: int
    filename: str
    metadata: dict = {}


class RetrievedDoc(BaseModel):
    """Represents a retrieved document with score."""
    id: str
    doc_id: str
    filename: str
    content: str
    score: float
    route: Literal["vector", "bm25", "hybrid"]
    chunk_index: Optional[int] = None


class QueryRequest(BaseModel):
    """Request model for query endpoint."""
    query: str = Field(..., description="The question to answer")
    top_k: Optional[int] = Field(None, description="Number of chunks to retrieve")


class SourceRef(BaseModel):
    """Source reference with citation information."""
    id: str
    filename: str
    score: float
    route: Literal["vector", "bm25", "hybrid"]


class QueryResponse(BaseModel):
    """Response model for query with sources."""
    answer: str
    sources: List[SourceRef]
    query: str


class UploadRequest(BaseModel):
    """Request model for document upload."""
    content: str
    filename: str
    doc_id: Optional[str] = None
    metadata: Optional[dict] = {}


class UploadResponse(BaseModel):
    """Response model for document upload."""
    doc_id: str
    filename: str
    chunks_created: int
    status: str


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    ollama_available: bool
    indices_loaded: bool


