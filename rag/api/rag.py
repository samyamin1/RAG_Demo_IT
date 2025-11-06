"""FastAPI REST API for RAG service."""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from rag.core.service import CentralizedRAGService
from rag.types import (
    QueryRequest,
    QueryResponse,
    UploadRequest,
    UploadResponse,
    HealthResponse,
)
from rag.config import settings, print_config

# Initialize FastAPI app
app = FastAPI(
    title="RAG API",
    description="Production-ready Retrieval Augmented Generation API with Ollama",
    version="1.0.0",
)

# Initialize RAG service (singleton)
rag_service = CentralizedRAGService()

# Print configuration on startup
@app.on_event("startup")
async def startup_event():
    """Print configuration on startup."""
    print_config()


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "message": "RAG API is running",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    
    Returns system status and availability of components.
    """
    status = rag_service.get_status()
    
    return HealthResponse(
        status=status["status"],
        ollama_available=status["ollama_available"],
        indices_loaded=status["indices_loaded"],
    )


@app.post("/upload", response_model=UploadResponse, tags=["Documents"])
async def upload_document(request: UploadRequest):
    """
    Upload and index a document.
    
    Accepts text content and processes it through the ingestion pipeline:
    - Parsing
    - Chunking
    - Embedding
    - Indexing (both vector and BM25)
    """
    try:
        result = rag_service.upload_document(
            content=request.content,
            filename=request.filename,
            doc_id=request.doc_id,
            metadata=request.metadata,
        )
        
        return UploadResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.post("/query", response_model=QueryResponse, tags=["Query"])
async def query_documents(request: QueryRequest):
    """
    Query documents with RAG.
    
    Performs hybrid retrieval (vector + BM25) with RRF fusion,
    then generates an answer using the local LLM with context.
    
    Returns the answer with cited sources.
    """
    try:
        response = rag_service.query_with_answer(
            query=request.query,
            top_k=request.top_k,
        )
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@app.delete("/delete", tags=["Documents"])
async def delete_document(doc_id: str = Query(..., description="Document ID to delete")):
    """
    Delete a document from all indices.
    
    Removes all chunks associated with the given document ID
    from both vector and BM25 stores.
    """
    try:
        rag_service.delete_document(doc_id)
        return {"status": "success", "doc_id": doc_id, "message": "Document deleted"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")


@app.get("/status", tags=["Health"])
async def get_status():
    """
    Get detailed system status.
    
    Returns information about:
    - Ollama availability
    - Model loaded
    - Index counts
    - Configuration
    """
    try:
        status = rag_service.get_status()
        return status
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")


@app.post("/reset", tags=["Admin"])
async def reset_indices():
    """
    Reset all indices (admin only).
    
    **WARNING**: This will delete all indexed documents!
    """
    try:
        rag_service.reset_indices()
        return {"status": "success", "message": "All indices reset"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reset failed: {str(e)}")


