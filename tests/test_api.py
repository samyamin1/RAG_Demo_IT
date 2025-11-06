"""Test FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient

from rag.api.rag import app

client = TestClient(app)


def test_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "docs" in data


def test_health():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "ollama_available" in data
    assert "indices_loaded" in data


def test_status():
    """Test status endpoint."""
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "ollama_model" in data


def test_upload_document():
    """Test document upload endpoint."""
    payload = {
        "content": "This is a test document about retrieval augmented generation.",
        "filename": "test_doc.txt",
    }
    
    response = client.post("/upload", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "doc_id" in data
    assert "chunks_created" in data
    assert data["status"] == "success"


def test_query_endpoint():
    """Test query endpoint."""
    # First upload a document
    upload_payload = {
        "content": "RAG combines retrieval with generation using LLMs.",
        "filename": "rag_info.txt",
    }
    client.post("/upload", json=upload_payload)
    
    # Now query
    query_payload = {
        "query": "What is RAG?",
        "top_k": 3,
    }
    
    response = client.post("/query", json=query_payload)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data
    assert "query" in data
    assert isinstance(data["sources"], list)


def test_delete_document():
    """Test document deletion endpoint."""
    # First upload a document
    upload_payload = {
        "content": "Document to be deleted.",
        "filename": "delete_me.txt",
        "doc_id": "test_delete_123",
    }
    response = client.post("/upload", json=upload_payload)
    assert response.status_code == 200
    
    # Now delete it
    response = client.delete("/delete?doc_id=test_delete_123")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["doc_id"] == "test_delete_123"


def test_invalid_query():
    """Test query with invalid payload."""
    payload = {
        # Missing required 'query' field
        "top_k": 5
    }
    
    response = client.post("/query", json=payload)
    assert response.status_code == 422  # Validation error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


