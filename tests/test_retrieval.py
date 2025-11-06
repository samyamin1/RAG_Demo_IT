"""Test retrieval components."""

import pytest
import tempfile
import shutil
from pathlib import Path

from rag.types import Chunk
from rag.retrieval.bm25 import BM25Store
from rag.retrieval.chroma import ChromaVectorStore
from rag.retrieval.hybrid import DocumentRetrievalService


@pytest.fixture
def temp_dirs():
    """Create temporary directories for testing."""
    chroma_dir = tempfile.mkdtemp()
    bm25_dir = tempfile.mkdtemp()
    yield chroma_dir, bm25_dir
    shutil.rmtree(chroma_dir, ignore_errors=True)
    shutil.rmtree(bm25_dir, ignore_errors=True)


@pytest.fixture
def sample_chunks():
    """Create sample chunks for testing."""
    return [
        Chunk(
            id="chunk_1",
            doc_id="doc_1",
            content="Retrieval augmented generation combines retrieval with LLMs",
            chunk_index=0,
            filename="doc1.txt",
            metadata={"title": "RAG Overview"}
        ),
        Chunk(
            id="chunk_2",
            doc_id="doc_1",
            content="Vector search uses embeddings to find similar documents",
            chunk_index=1,
            filename="doc1.txt",
            metadata={"title": "RAG Overview"}
        ),
        Chunk(
            id="chunk_3",
            doc_id="doc_2",
            content="BM25 is a keyword-based ranking function for text retrieval",
            chunk_index=0,
            filename="doc2.txt",
            metadata={"title": "BM25 Basics"}
        ),
    ]


def test_bm25_store_basic(temp_dirs, sample_chunks):
    """Test basic BM25 store operations."""
    _, bm25_dir = temp_dirs
    store = BM25Store(persist_directory=bm25_dir)
    
    # Add chunks
    store.add_chunks(sample_chunks)
    
    # Check count
    assert store.count() == 3
    
    # Search
    results = store.search("retrieval generation", k=2)
    assert len(results) <= 2
    assert all(r.route == "bm25" for r in results)


def test_bm25_persistence(temp_dirs, sample_chunks):
    """Test BM25 store persistence."""
    _, bm25_dir = temp_dirs
    
    # Create and populate store
    store1 = BM25Store(persist_directory=bm25_dir)
    store1.add_chunks(sample_chunks)
    count1 = store1.count()
    
    # Create new instance (should load from disk)
    store2 = BM25Store(persist_directory=bm25_dir)
    count2 = store2.count()
    
    assert count1 == count2


def test_bm25_delete_document(temp_dirs, sample_chunks):
    """Test document deletion from BM25 store."""
    _, bm25_dir = temp_dirs
    store = BM25Store(persist_directory=bm25_dir)
    store.add_chunks(sample_chunks)
    
    # Delete document
    store.delete_document("doc_1")
    
    # Should only have chunks from doc_2
    assert store.count() == 1
    remaining = [c for c in store.chunks if c.doc_id == "doc_2"]
    assert len(remaining) == 1


@pytest.mark.skipif(
    not Path(".chroma").exists(),
    reason="Requires initialized ChromaDB"
)
def test_hybrid_retrieval(temp_dirs, sample_chunks):
    """Test hybrid retrieval service."""
    chroma_dir, bm25_dir = temp_dirs
    
    service = DocumentRetrievalService(
        chroma_dir=chroma_dir,
        bm25_dir=bm25_dir,
    )
    
    # Create dummy embeddings (normally from embedding model)
    embeddings = [[0.1] * 384 for _ in sample_chunks]
    
    # Add chunks
    service.add_chunks(sample_chunks, embeddings)
    
    # Check counts
    counts = service.count()
    assert counts["bm25"] == 3
    
    # Query
    results = service.query_documents("retrieval generation", top_k=2)
    assert len(results) <= 2
    assert all(r.route in ["vector", "bm25", "hybrid"] for r in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


