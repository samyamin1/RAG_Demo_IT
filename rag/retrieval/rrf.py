"""Reciprocal Rank Fusion (RRF) implementation."""

from typing import List, Dict, Tuple, Optional
from rag.types import RetrievedDoc
from rag.config import settings


def reciprocal_rank_fusion(
    vector_results: List[RetrievedDoc],
    bm25_results: List[RetrievedDoc],
    k: int = 60,
    top_k: Optional[int] = None,
) -> List[RetrievedDoc]:
    """
    Merge vector and BM25 results using Reciprocal Rank Fusion.
    
    RRF formula: score = sum(1 / (k + rank_i)) for all rankings
    
    Args:
        vector_results: Results from vector similarity search
        bm25_results: Results from BM25 lexical search
        k: RRF constant (default 60)
        top_k: Number of top results to return
        
    Returns:
        Fused and re-ranked results
    """
    from typing import Optional
    
    if top_k is None:
        top_k = settings.top_k
    
    # Build score dict keyed by chunk ID
    rrf_scores: Dict[str, float] = {}
    doc_map: Dict[str, RetrievedDoc] = {}
    
    # Add vector results
    for rank, doc in enumerate(vector_results, start=1):
        rrf_scores[doc.id] = rrf_scores.get(doc.id, 0.0) + (1.0 / (k + rank))
        if doc.id not in doc_map:
            doc_map[doc.id] = doc
    
    # Add BM25 results
    for rank, doc in enumerate(bm25_results, start=1):
        rrf_scores[doc.id] = rrf_scores.get(doc.id, 0.0) + (1.0 / (k + rank))
        if doc.id not in doc_map:
            doc_map[doc.id] = doc
    
    # Sort by RRF score
    sorted_ids = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)
    
    # Build result list
    results = []
    for doc_id in sorted_ids[:top_k]:
        doc = doc_map[doc_id]
        # Update score and route
        fused_doc = RetrievedDoc(
            id=doc.id,
            doc_id=doc.doc_id,
            filename=doc.filename,
            content=doc.content,
            score=rrf_scores[doc_id],
            route="hybrid",  # Mark as hybrid since it's fused
            chunk_index=doc.chunk_index,
        )
        results.append(fused_doc)
    
    return results


def calculate_rrf_score(ranks: List[int], k: int = 60) -> float:
    """
    Calculate RRF score for a document given its ranks in multiple lists.
    
    Args:
        ranks: List of ranks (1-indexed) for this document
        k: RRF constant
        
    Returns:
        RRF score
    """
    return sum(1.0 / (k + rank) for rank in ranks)


