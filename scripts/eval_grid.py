"""Evaluation grid search for parameter tuning."""

import sys
import json
import itertools
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.core.service import CentralizedRAGService
from rag.config import settings


# Evaluation questions with expected document IDs/keywords
EVAL_SET = [
    {
        "question": "What is retrieval augmented generation?",
        "expected_keywords": ["retrieval", "rag", "generation", "llm"],
    },
    {
        "question": "How does vector search work?",
        "expected_keywords": ["vector", "embedding", "similarity", "search"],
    },
    {
        "question": "What is BM25 scoring?",
        "expected_keywords": ["bm25", "keyword", "lexical", "score"],
    },
]


def evaluate_retrieval(
    rag_service: CentralizedRAGService,
    top_k: int = 5,
    vector_top_k: int = 10,
    bm25_top_k: int = 20,
    rrf_k: int = 60,
) -> Dict[str, float]:
    """
    Evaluate retrieval quality.
    
    Args:
        rag_service: RAG service instance
        top_k: Final results count
        vector_top_k: Vector candidates
        bm25_top_k: BM25 candidates
        rrf_k: RRF fusion parameter
        
    Returns:
        Evaluation metrics
    """
    total_hits = 0
    total_scores = []
    
    for item in EVAL_SET:
        question = item["question"]
        expected_keywords = item["expected_keywords"]
        
        # Retrieve documents
        retrieved = rag_service.retrieval_service.query_documents(
            query=question,
            top_k=top_k,
            vector_top_k=vector_top_k,
            bm25_top_k=bm25_top_k,
            rrf_k=rrf_k,
        )
        
        # Check if any expected keyword is in retrieved content
        hit = False
        for doc in retrieved:
            content_lower = doc.content.lower()
            if any(kw in content_lower for kw in expected_keywords):
                hit = True
                total_scores.append(doc.score)
                break
        
        if hit:
            total_hits += 1
    
    # Calculate metrics
    hit_rate = total_hits / len(EVAL_SET) if EVAL_SET else 0.0
    avg_score = sum(total_scores) / len(total_scores) if total_scores else 0.0
    
    return {
        "hit_rate": hit_rate,
        "avg_score": avg_score,
        "total_queries": len(EVAL_SET),
        "hits": total_hits,
    }


def run_grid_search():
    """Run parameter grid search."""
    print("\n" + "="*70)
    print(" " * 20 + "PARAMETER EVALUATION")
    print("="*70)
    
    # Define parameter grid
    param_grid = {
        "top_k": [4, 5, 6],
        "vector_top_k": [8, 10, 12],
        "bm25_top_k": [15, 20, 25],
        "rrf_k": [50, 60, 70],
    }
    
    print(f"\nParameter grid:")
    for param, values in param_grid.items():
        print(f"  {param}: {values}")
    
    # Initialize RAG service
    rag_service = CentralizedRAGService()
    
    # Check if indices are loaded
    status = rag_service.get_status()
    if not status['indices_loaded']:
        print("\n⚠ Warning: No documents indexed!")
        print("Please run: python scripts/index_documents.py --rebuild")
        return
    
    # Run grid search
    print(f"\nRunning evaluation...")
    print(f"Eval epochs: {settings.eval_epochs}")
    
    results = []
    
    # Generate all parameter combinations
    keys = list(param_grid.keys())
    values = list(param_grid.values())
    combinations = list(itertools.product(*values))
    
    print(f"Total combinations: {len(combinations)}\n")
    
    for i, combo in enumerate(combinations, 1):
        params = dict(zip(keys, combo))
        
        # Run multiple epochs and average
        epoch_results = []
        for epoch in range(settings.eval_epochs):
            metrics = evaluate_retrieval(rag_service, **params)
            epoch_results.append(metrics)
        
        # Average metrics across epochs
        avg_hit_rate = sum(r["hit_rate"] for r in epoch_results) / settings.eval_epochs
        avg_score = sum(r["avg_score"] for r in epoch_results) / settings.eval_epochs
        
        result = {
            **params,
            "hit_rate": avg_hit_rate,
            "avg_score": avg_score,
        }
        results.append(result)
        
        print(f"[{i}/{len(combinations)}] {params} → hit_rate={avg_hit_rate:.3f}, avg_score={avg_score:.3f}")
    
    # Sort by hit rate
    results.sort(key=lambda x: (x["hit_rate"], x["avg_score"]), reverse=True)
    
    # Print top 5
    print("\n" + "="*70)
    print("TOP 5 CONFIGURATIONS")
    print("="*70)
    for i, result in enumerate(results[:5], 1):
        print(f"\n{i}. Hit Rate: {result['hit_rate']:.3f}, Avg Score: {result['avg_score']:.3f}")
        print(f"   Parameters:")
        for key in keys:
            print(f"     {key}: {result[key]}")
    
    # Save results
    output_file = "eval_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "="*70)
    print(f"Results saved to: {output_file}")
    print("="*70 + "\n")


if __name__ == "__main__":
    run_grid_search()


