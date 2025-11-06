"""Test RRF (Reciprocal Rank Fusion) implementation."""

import pytest
from rag.retrieval.rrf import reciprocal_rank_fusion, calculate_rrf_score
from rag.types import RetrievedDoc


def test_rrf_basic_fusion():
    """Test basic RRF fusion with two lists."""
    # Create mock vector results
    vector_results = [
        RetrievedDoc(
            id="chunk_1",
            doc_id="doc_1",
            filename="doc1.txt",
            content="Content 1",
            score=0.9,
            route="vector",
        ),
        RetrievedDoc(
            id="chunk_2",
            doc_id="doc_2",
            filename="doc2.txt",
            content="Content 2",
            score=0.8,
            route="vector",
        ),
    ]
    
    # Create mock BM25 results
    bm25_results = [
        RetrievedDoc(
            id="chunk_2",  # Same as vector rank 2
            doc_id="doc_2",
            filename="doc2.txt",
            content="Content 2",
            score=10.5,
            route="bm25",
        ),
        RetrievedDoc(
            id="chunk_3",
            doc_id="doc_3",
            filename="doc3.txt",
            content="Content 3",
            score=9.2,
            route="bm25",
        ),
    ]
    
    # Fuse results
    fused = reciprocal_rank_fusion(vector_results, bm25_results, k=60, top_k=3)
    
    # Check that chunk_2 is ranked higher (appears in both lists)
    assert fused[0].id == "chunk_2", "Chunk appearing in both lists should rank first"
    assert fused[0].route == "hybrid", "Fused results should have 'hybrid' route"
    assert len(fused) == 3, "Should return top_k results"


def test_calculate_rrf_score():
    """Test RRF score calculation."""
    # Document at rank 1 in both lists
    score = calculate_rrf_score([1, 1], k=60)
    expected = 2 * (1.0 / 61)
    assert abs(score - expected) < 1e-6
    
    # Document at different ranks
    score = calculate_rrf_score([1, 5], k=60)
    expected = (1.0 / 61) + (1.0 / 65)
    assert abs(score - expected) < 1e-6


def test_rrf_empty_lists():
    """Test RRF with empty lists."""
    fused = reciprocal_rank_fusion([], [], k=60, top_k=5)
    assert len(fused) == 0, "Empty input should return empty result"


def test_rrf_single_list():
    """Test RRF with only vector results."""
    vector_results = [
        RetrievedDoc(
            id="chunk_1",
            doc_id="doc_1",
            filename="doc1.txt",
            content="Content 1",
            score=0.9,
            route="vector",
        ),
    ]
    
    fused = reciprocal_rank_fusion(vector_results, [], k=60, top_k=5)
    assert len(fused) == 1
    assert fused[0].id == "chunk_1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


