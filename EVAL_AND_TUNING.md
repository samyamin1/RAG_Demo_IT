# Evaluation and Tuning Guide

Guide for evaluating RAG performance and systematic parameter tuning.

## Table of Contents

1. [Overview](#overview)
2. [Running Evaluations](#running-evaluations)
3. [Metrics](#metrics)
4. [Grid Search](#grid-search)
5. [Manual Testing](#manual-testing)
6. [Continuous Improvement](#continuous-improvement)

---

## Overview

Evaluation helps answer:
- ✅ Is retrieval finding the right documents?
- ✅ Are answers grounded in sources?
- ✅ How do parameter changes affect quality?

### Key Concepts

**Epochs:** In this RAG system, "epochs" means **repeated evaluation runs** for statistical stability, NOT model training. We're evaluating a fixed system multiple times to average out randomness.

**Hit Rate@K:** Fraction of queries where at least one expected document appears in top-K results.

**Avg Score:** Average relevance score of supporting documents.

---

## Running Evaluations

### Quick Eval

```bash
# Run default evaluation
make eval

# Or directly
python scripts/eval_grid.py
```

**Output:**
```
======================================================================
                      PARAMETER EVALUATION
======================================================================

Parameter grid:
  top_k: [4, 5, 6]
  vector_top_k: [8, 10, 12]
  bm25_top_k: [15, 20, 25]
  rrf_k: [50, 60, 70]

Running evaluation...
Eval epochs: 3
Total combinations: 27

[1/27] {'top_k': 4, 'vector_top_k': 8, ...} → hit_rate=0.667, avg_score=0.734
[2/27] {'top_k': 4, 'vector_top_k': 8, ...} → hit_rate=0.667, avg_score=0.721
...
[27/27] {'top_k': 6, 'vector_top_k': 12, ...} → hit_rate=1.000, avg_score=0.812

======================================================================
TOP 5 CONFIGURATIONS
======================================================================

1. Hit Rate: 1.000, Avg Score: 0.812
   Parameters:
     top_k: 6
     vector_top_k: 12
     bm25_top_k: 25
     rrf_k: 60

...
```

---

## Metrics

### Hit Rate@K

**Definition:** Percentage of queries where at least one expected document appears in top-K results.

**Formula:**
```
hit_rate = (queries_with_hit / total_queries)
```

**Example:**
```
Eval set: 10 queries
Hits: 8 queries found expected doc in top-5
Hit Rate@5 = 8/10 = 0.80 (80%)
```

**Interpretation:**
- **0.9-1.0:** Excellent - retrieval is working well
- **0.7-0.9:** Good - may need tuning
- **<0.7:** Poor - check indexing or parameters

**How to Improve:**
- ↑ `TOP_K`, `VECTOR_TOP_K`, `BM25_TOP_K`
- Adjust `RRF_K`
- Re-check query embeddings

---

### Average Score

**Definition:** Average relevance score of the supporting (hit) documents.

**Why It Matters:**
- Higher score → More confident retrieval
- Can distinguish between "barely relevant" and "highly relevant"

**Interpretation:**
- **>0.8:** High confidence matches
- **0.6-0.8:** Moderate confidence
- **<0.6:** Weak matches (may need parameter tuning)

**How to Improve:**
- Better chunking (`CHUNK_SIZE`, `CHUNK_OVERLAP`)
- Tune BM25 parameters (`K1`, `B`)
- Improve embeddings (use different model)

---

## Grid Search

### Default Grid

```python
param_grid = {
    "top_k": [4, 5, 6],
    "vector_top_k": [8, 10, 12],
    "bm25_top_k": [15, 20, 25],
    "rrf_k": [50, 60, 70],
}
```

This tests 3×3×3×3 = **81 combinations**

### Custom Grid

Edit `scripts/eval_grid.py`:

```python
# Example: Focus on TOP_K tuning
param_grid = {
    "top_k": [3, 4, 5, 6, 7, 8],  # Main variable
    "vector_top_k": [10],          # Fixed
    "bm25_top_k": [20],            # Fixed
    "rrf_k": [60],                 # Fixed
}
```

### Interpreting Results

**Example Output:**
```
TOP 5 CONFIGURATIONS

1. Hit Rate: 1.000, Avg Score: 0.812
   Parameters: top_k=6, vector_top_k=12, bm25_top_k=25, rrf_k=60

2. Hit Rate: 1.000, Avg Score: 0.805
   Parameters: top_k=6, vector_top_k=10, bm25_top_k=25, rrf_k=60

3. Hit Rate: 0.933, Avg Score: 0.798
   Parameters: top_k=5, vector_top_k=12, bm25_top_k=25, rrf_k=60
```

**Analysis:**
- Configs 1 & 2: Perfect hit rate, choose based on avg_score
- Config 1 wins slightly (0.812 vs 0.805)
- Observation: `vector_top_k=12` seems beneficial

**Next Steps:**
1. Update `.env` with best config
2. Run `make demo` to verify improvement
3. Test on real queries

---

## Manual Testing

### Define Test Cases

Create `test_cases.json`:

```json
[
  {
    "query": "What is retrieval augmented generation?",
    "expected_keywords": ["retrieval", "rag", "llm", "generation"],
    "expected_doc_ids": ["doc_023", "doc_045"]
  },
  {
    "query": "How does BM25 scoring work?",
    "expected_keywords": ["bm25", "keyword", "term frequency"],
    "expected_doc_ids": ["doc_089"]
  }
]
```

### Run Manual Tests

```python
from rag.core.service import CentralizedRAGService

rag = CentralizedRAGService()

# Test query
response = rag.query_with_answer("What is RAG?")

# Check sources
print(f"Answer: {response.answer[:200]}...")
print(f"\nSources:")
for src in response.sources:
    print(f"  - {src.filename} (score: {src.score:.3f}, route: {src.route})")

# Verify expected docs appear
expected_ids = ["doc_023", "doc_045"]
retrieved_ids = [src.id for src in response.sources]

hits = [exp_id for exp_id in expected_ids if any(exp_id in ret_id for ret_id in retrieved_ids)]
print(f"\nHits: {len(hits)}/{len(expected_ids)}")
```

---

### A/B Testing

Compare two configurations:

```bash
# Configuration A (baseline)
echo "TOP_K=5" > .env.config_a
echo "VECTOR_TOP_K=10" >> .env.config_a
echo "BM25_TOP_K=20" >> .env.config_a

# Configuration B (experimental)
echo "TOP_K=6" > .env.config_b
echo "VECTOR_TOP_K=12" >> .env.config_b
echo "BM25_TOP_K=25" >> .env.config_b

# Test A
cp .env.config_a .env
make demo > results_a.txt

# Test B
cp .env.config_b .env
make demo > results_b.txt

# Compare
diff results_a.txt results_b.txt
```

---

## Continuous Improvement

### Workflow

```
1. Collect real user queries
   ↓
2. Identify failure cases
   ↓
3. Add to eval set (scripts/eval_grid.py)
   ↓
4. Run grid search
   ↓
5. Update .env with best config
   ↓
6. Validate on real queries
   ↓
7. Monitor performance
   ↓
8. Repeat monthly/quarterly
```

---

### Example: Adding New Test Case

**Step 1: User reports bad answer**

Query: "What are the benefits of vector search?"
Expected: doc_134, doc_178
Got: doc_045 (unrelated)

**Step 2: Add to eval set**

Edit `scripts/eval_grid.py`:

```python
EVAL_SET = [
    # ... existing cases ...
    {
        "question": "What are the benefits of vector search?",
        "expected_keywords": ["vector", "semantic", "similarity", "benefits"],
    },
]
```

**Step 3: Re-run eval**

```bash
make eval
```

**Step 4: Analyze**

If hit rate drops, identify which parameter change helps:
- Try ↑ `VECTOR_TOP_K`
- Try ↑ `TOP_K`
- Check if doc_134/doc_178 are even indexed

**Step 5: Update config**

```bash
# In .env
VECTOR_TOP_K=12  # was 10
```

**Step 6: Validate**

```bash
make demo
# Manually test the failing query
```

---

## Advanced Evaluation

### Custom Metrics

Add to `scripts/eval_grid.py`:

```python
def calculate_mrr(retrieved_ids, expected_ids):
    """Mean Reciprocal Rank"""
    for rank, doc_id in enumerate(retrieved_ids, start=1):
        if doc_id in expected_ids:
            return 1.0 / rank
    return 0.0

def calculate_precision_at_k(retrieved_ids, expected_ids, k):
    """Precision@K"""
    relevant = sum(1 for doc_id in retrieved_ids[:k] if doc_id in expected_ids)
    return relevant / k
```

### Answer Quality Evaluation

Use LLM-as-judge:

```python
from rag.llm.ollama_wrapper import LocalLLMWrapper

llm = LocalLLMWrapper()

judge_prompt = f"""
Rate the following answer on a scale of 1-5 for:
1. Accuracy
2. Citation quality
3. Completeness

Question: {query}
Answer: {answer}
Sources: {sources}

Provide a JSON score.
"""

score = llm.generate_response(judge_prompt, temperature=0.1)
print(score)
```

---

## Benchmarking

### Performance Benchmarks

```bash
# Time 100 queries
python -m timeit -n 100 "from rag.core.service import CentralizedRAGService; CentralizedRAGService().query_with_answer('test')"
```

### Latency Breakdown

Add timing to `rag/core/service.py`:

```python
import time

def query_with_answer(self, query, top_k=None, temperature=None):
    t0 = time.time()
    
    # Retrieval
    retrieved_docs = self.retrieval_service.query_documents(query, top_k)
    t1 = time.time()
    print(f"Retrieval: {t1-t0:.2f}s")
    
    # Context assembly
    context = self.context_assembler.build_prompt_context(retrieved_docs, query)
    t2 = time.time()
    print(f"Context: {t2-t1:.2f}s")
    
    # Generation
    answer = self.llm.generate_response(...)
    t3 = time.time()
    print(f"Generation: {t3-t2:.2f}s")
    
    print(f"Total: {t3-t0:.2f}s")
    ...
```

---

## Experiment Tracking

### Log Results

Create `experiments.json`:

```json
{
  "experiment_1": {
    "date": "2025-11-05",
    "config": {
      "top_k": 5,
      "vector_top_k": 10,
      "bm25_top_k": 20,
      "rrf_k": 60
    },
    "metrics": {
      "hit_rate": 0.867,
      "avg_score": 0.745,
      "latency_p50": 2.3,
      "latency_p95": 4.1
    }
  },
  "experiment_2": {
    "date": "2025-11-06",
    "config": {
      "top_k": 6,
      "vector_top_k": 12,
      "bm25_top_k": 25,
      "rrf_k": 60
    },
    "metrics": {
      "hit_rate": 0.933,
      "avg_score": 0.812,
      "latency_p50": 2.7,
      "latency_p95": 4.8
    }
  }
}
```

**Analysis:**
- Experiment 2: +7.6% hit rate, +9% avg score
- Trade-off: +17% latency (p50)
- Decision: Accept latency for quality improvement

---

## Summary

### Evaluation Checklist

- [ ] Define eval set with diverse queries
- [ ] Run baseline (`make eval`)
- [ ] Identify weaknesses (low hit rate, low scores)
- [ ] Tune parameters systematically (one at a time)
- [ ] Re-run eval after each change
- [ ] Document best config in `.env`
- [ ] Monitor real-world performance
- [ ] Update eval set as new failure cases emerge

### Key Takeaways

1. **Start simple**: Use default params, establish baseline
2. **Measure first**: Don't tune blindly
3. **One variable at a time**: Isolate parameter effects
4. **Track experiments**: Log configs and results
5. **Validate on real queries**: Don't overfit to eval set
6. **Iterate**: Continuous improvement over time

---

**Related Docs:**
- [PARAMETERS.md](PARAMETERS.md) - Parameter descriptions and tuning tips
- [ARCHITECTURE.md](ARCHITECTURE.md) - System components
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues

---

**Pro Tip:** Run `make eval` weekly to catch performance regressions!


