# RAG System Parameters Guide

Complete guide to tuning RAG parameters for optimal performance.

## Table of Contents

1. [Overview](#overview)
2. [Retrieval & Fusion Parameters](#1-retrieval--fusion-parameters)
3. [Chunking Parameters](#2-chunking-parameters)
4. [LLM Generation Parameters](#3-llm-generation-parameters)
5. [Evaluation Parameters](#4-evaluation--epochs)
6. [How to Use Parameters](#5-how-to-use-parameters-to-get-better-rag-results)
7. [Parameter Interaction](#6-parameter-interactions)
8. [Example Configurations](#7-example-configurations)

---

## Overview

RAG performance depends on carefully tuned parameters across retrieval, chunking, and generation stages. This guide explains **WHAT** each parameter does, **WHY** it matters, **HOW** to change it, and **tuning strategies**.

### Quick Reference

| Category | Key Parameters | When to Tune |
|----------|----------------|--------------|
| **Retrieval** | TOP_K, VECTOR_TOP_K, BM25_TOP_K, RRF_K | Missing facts or noisy answers |
| **Chunking** | CHUNK_SIZE, CHUNK_OVERLAP | Context boundaries or dilution |
| **Generation** | TEMPERATURE, MAX_CONTEXT_TOKENS | Answer quality or hallucinations |
| **BM25** | BM25_K1, BM25_B | Keyword matching issues |

---

## 1. Retrieval & Fusion Parameters

### Parameter Table

| Param | Where | Default | How to Set | What It Does | Tuning Tips |
|-------|-------|---------|------------|--------------|-------------|
| `TOP_K` | .env, API | 5 | `.env` or `/query?top_k=` | Number of chunks retrieved overall (after fusion) | Start 4-8; raise if answers miss facts; lower if context gets noisy |
| `VECTOR_TOP_K` | .env | 10 | `.env` | Pre-fusion vector candidate count | 8-20; more = slower but better recall |
| `BM25_TOP_K` | .env | 20 | `.env` | Pre-fusion lexical candidate count | 10-40 depending on corpus size |
| `RRF_K` | .env | 60 | `.env` | RRF dampening factor for merging vector+BM25 ranks | 50-80 common; increase if rankers disagree |
| `BM25_K1` | .env | 1.5 | `.env` | BM25 term frequency saturation | 1.2-2.0; higher = more weight to term frequency |
| `BM25_B` | .env | 0.75 | `.env` | BM25 length normalization | 0.5-0.9; raise if long docs dominate |

### TOP_K

**What:** Final number of chunks returned to the LLM after RRF fusion.

**Why:** Controls context size vs quality tradeoff
- **Too low** (1-3): May miss supporting evidence
- **Too high** (10+): Context dilution, slower generation, token limit issues

**How to Set:**
```bash
# In .env
TOP_K=5

# Via API
curl -X POST "/query" -d '{"query": "...", "top_k": 6}'

# Override at runtime
TOP_K=6 python scripts/demo_wrong_right.py
```

**Tuning Strategy:**
1. Start with 5
2. If answers lack detail → increase to 6-8
3. If answers become vague/unfocused → decrease to 3-4
4. Monitor context token usage (see logs)

**Example:**
```bash
# Precision mode (stricter)
TOP_K=3 make demo

# Recall mode (comprehensive)
TOP_K=8 make demo
```

---

### VECTOR_TOP_K

**What:** Number of candidates from vector similarity search *before* RRF fusion.

**Why:** Vector search captures semantic similarity but may need overcomplete candidate set for fusion to work well.

**Recommended Ratio:** `VECTOR_TOP_K ≈ 2 × TOP_K`

**Tuning:**
- ↑ if vector-only results would be good but hybrid misses them
- ↓ if embedding step is slow or vector results are noisy

**Example:**
```bash
# Standard: retrieve 10 vector candidates, fuse to top 5
VECTOR_TOP_K=10
TOP_K=5

# High recall: retrieve 16 vector candidates
VECTOR_TOP_K=16
TOP_K=5
```

---

### BM25_TOP_K

**What:** Number of candidates from BM25 keyword search *before* RRF fusion.

**Why:** BM25 excels at exact term matching but can return many marginal results. Larger candidate pool ensures good lexical matches make it to fusion.

**Recommended Ratio:** `BM25_TOP_K ≈ 3-4 × TOP_K`

**Tuning:**
- ↑ if queries have specific keywords that should match (technical terms, names, codes)
- ↓ if BM25 pollutes results with keyword spam

**Example:**
```bash
# Keyword-heavy queries (e.g., product codes, API names)
BM25_TOP_K=30

# Semantic queries (e.g., "explain the concept of...")
BM25_TOP_K=15
```

---

### RRF_K

**What:** Dampening constant in Reciprocal Rank Fusion formula:
```
score(doc) = Σ [ 1 / (RRF_K + rank) ]
```

**Why:** 
- **Lower RRF_K** (30-50): Aggressive, top-ranked items dominate
- **Higher RRF_K** (70-90): Conservative, smoother rank blending

**Default:** 60 (established in literature)

**Tuning:**
- ↑ if vector and BM25 frequently disagree and you want to give lower-ranked items more chance
- ↓ if you trust the top results from each ranker

**Example:**
```bash
# Aggressive fusion (trust top ranks)
RRF_K=50

# Conservative fusion (blend more evenly)
RRF_K=70
```

**Visual:**
```
RRF_K=30:  Rank 1: 0.032, Rank 5: 0.029  (steep drop)
RRF_K=60:  Rank 1: 0.016, Rank 5: 0.015  (gentle)
RRF_K=90:  Rank 1: 0.011, Rank 5: 0.011  (very gentle)
```

---

### BM25_K1

**What:** BM25 term frequency saturation parameter.

**Formula:**
```
TF_component = (k1 + 1) × tf / (k1 + tf)
```

**Why:**
- **Higher K1** (1.8-2.0): Rewards repeated term occurrences more
- **Lower K1** (1.2-1.4): Diminishing returns for repetition

**Default:** 1.5

**Tuning:**
- ↑ if important terms are repeated in relevant docs
- ↓ if spam/keyword stuffing is an issue

**Example:**
```bash
# Technical docs with repeated keywords
BM25_K1=1.8

# Natural language, avoid repetition bias
BM25_K1=1.2
```

---

### BM25_B

**What:** BM25 length normalization parameter.

**Formula:**
```
Length_norm = (1 - B) + B × (doc_length / avg_doc_length)
```

**Why:**
- **Higher B** (0.8-0.9): Penalize long documents more
- **Lower B** (0.5-0.7): Length matters less

**Default:** 0.75

**Tuning:**
- ↑ if long documents dominate results unfairly
- ↓ if long documents are genuinely comprehensive

**Example:**
```bash
# Penalize verbose docs
BM25_B=0.85

# Don't penalize comprehensive docs
BM25_B=0.65
```

---

## 2. Chunking Parameters

### Parameter Table

| Param | Where | Default | Tuning Tips |
|-------|-------|---------|-------------|
| `CHUNK_SIZE` | .env | 800 tokens | 500-1200; longer preserves context but risks dilution + exceeding window |
| `CHUNK_OVERLAP` | .env | 120 tokens | 80-200; increase if answers miss boundary info |
| `SPLITTER` | code | `recursive` | Keep recursive; switch to semantic if headings are strong |

---

### CHUNK_SIZE

**What:** Target number of tokens per chunk (rough heuristic: chars / 4).

**Why:**
- **Smaller chunks** (400-600): Fine-grained retrieval, faster embeddings, but may break context
- **Larger chunks** (1000-1500): Preserve context, but dilute relevance and risk exceeding LLM window

**Default:** 800 tokens (~3200 characters)

**How to Set:**
```bash
# In .env
CHUNK_SIZE=800

# Override at indexing
CHUNK_SIZE=600 python scripts/index_documents.py --rebuild
```

**Tuning Strategy:**

| Use Case | Recommended CHUNK_SIZE |
|----------|------------------------|
| Short FAQs | 400-600 |
| Technical docs | 800-1000 |
| Long-form articles | 1000-1500 |
| Code snippets | 200-400 |

**Trade-offs:**

```
Smaller Chunks (500):
  ✅ Precise retrieval
  ✅ Faster embeddings
  ❌ May break context
  ❌ More chunks = more storage

Larger Chunks (1200):
  ✅ Preserve context
  ✅ Fewer chunks
  ❌ Diluted relevance
  ❌ Risk exceeding context window
```

**Example:**
```bash
# For precise Q&A
CHUNK_SIZE=600
CHUNK_OVERLAP=100

# For comprehensive articles
CHUNK_SIZE=1000
CHUNK_OVERLAP=150
```

---

### CHUNK_OVERLAP

**What:** Number of tokens that overlap between consecutive chunks.

**Why:** Prevents information loss at chunk boundaries. Critical when answers span two chunks.

**Recommended Ratio:** `OVERLAP ≈ 10-20% of CHUNK_SIZE`

**Tuning:**
- ↑ if answers consistently miss info "between" chunks
- ↓ if redundancy is causing confusion

**Example:**
```bash
# Standard
CHUNK_SIZE=800
CHUNK_OVERLAP=120  # 15%

# High overlap for critical boundaries
CHUNK_SIZE=800
CHUNK_OVERLAP=200  # 25%
```

**Visual:**
```
Chunk 1: [=============================]
Chunk 2:                [=============================]
         |--------------| = OVERLAP
```

---

## 3. LLM Generation Parameters

### Parameter Table

| Param | Where | Default | Tuning Tips |
|-------|-------|---------|-------------|
| `OLLAMA_MODEL` | .env | `llama3:8b` | Try `llama3.1:8b` or `mistral` for latency/quality tradeoffs |
| `TEMPERATURE` | .env | 0.2 | 0.1-0.4 for factual tasks; raise for ideation |
| `MAX_CONTEXT_TOKENS` | .env | 6000 | Keep margin for system + prompt + answer; trim context accordingly |
| `MAX_OUTPUT_TOKENS` | .env | 1024 | Increase for longer answers, decrease for concise |
| `STOP_SEQS` | code | `[]` | Add if model drifts into citations block; e.g., `["\n\nSources:"]` |

---

### OLLAMA_MODEL

**What:** Which Ollama model to use for generation and (optionally) embeddings.

**Options:**

| Model | Size | RAM | Speed | Quality | Use Case |
|-------|------|-----|-------|---------|----------|
| `llama3:8b` | 4.7GB | 8GB+ | Fast | High | Default, balanced |
| `llama3.1:8b` | 4.7GB | 8GB+ | Fast | Higher | Improved reasoning |
| `mistral:7b` | 4.1GB | 8GB+ | Fastest | Good | Speed-critical |
| `llama3:70b` | 40GB | 64GB+ | Slow | Highest | Max quality |

**How to Set:**
```bash
# In .env
OLLAMA_MODEL=llama3:8b

# Pull new model
ollama pull llama3.1:8b

# Update .env
OLLAMA_MODEL=llama3.1:8b

# Restart API
make run
```

---

### TEMPERATURE

**What:** Sampling randomness. Lower = more deterministic, higher = more creative.

**Range:** 0.0 - 2.0 (practical: 0.1 - 1.0)

**Why:**
- **Low temp** (0.1-0.3): Factual, consistent, repetitive
- **High temp** (0.7-1.0): Creative, varied, riskier

**Default:** 0.2 (factual RAG tasks)

**Tuning:**

| Task | Recommended TEMPERATURE |
|------|-------------------------|
| Factual Q&A | 0.1 - 0.2 |
| Explanations | 0.2 - 0.4 |
| Summaries | 0.3 - 0.5 |
| Creative writing | 0.7 - 1.0 |

**Example:**
```bash
# Ultra-factual (deterministic)
TEMPERATURE=0.1

# Balanced
TEMPERATURE=0.2

# More varied phrasing
TEMPERATURE=0.4
```

---

### MAX_CONTEXT_TOKENS

**What:** Budget for context (retrieved chunks + system prompt + query).

**Why:** Must fit within model's context window (e.g., 8k for llama3) while leaving room for output.

**Calculation:**
```
Total window = 8192 tokens (for llama3)
Reserve for output = 1024 tokens
Reserve for system + query = 500 tokens
→ MAX_CONTEXT_TOKENS ≈ 6000
```

**Tuning:**
- ↑ if chunks are being cut off prematurely
- ↓ if hitting context window errors

**How to Set:**
```bash
# In .env
MAX_CONTEXT_TOKENS=6000

# For longer outputs
MAX_CONTEXT_TOKENS=5000
MAX_OUTPUT_TOKENS=2048
```

---

## 4. Evaluation / "Epochs"

### Parameter Table

| Param | Where | Default | Tuning Tips |
|-------|-------|---------|-------------|
| `EVAL_EPOCHS` | .env, CLI | 3 | Number of repeated eval passes for stability (not training!) |
| `GRID` | CLI | none | Comma-lists for exploring TOP_K, CHUNK_SIZE, RRF_K, BM25_K1/B |

**Note:** "Epochs" here means **repeated evaluation runs** for statistical stability, NOT model training.

### EVAL_EPOCHS

**What:** Number of times to run evaluation queries to average out variability.

**Why:** Ollama generation has some randomness even with low temperature.

**Example:**
```bash
# In .env
EVAL_EPOCHS=3

# Or via CLI
python scripts/eval_grid.py --epochs 5
```

---

## 5. How to Use Parameters to Get Better RAG Results

### Problem-Solution Matrix

| Problem | Symptoms | Solution |
|---------|----------|----------|
| **Missing Facts** | Answer lacks info you know is in docs | ↑ `VECTOR_TOP_K`, ↑ `BM25_TOP_K`, ↑ `TOP_K` by 1-2 |
| **Noisy Answers** | Irrelevant info, vague answers | ↓ `TOP_K`, ↓ `CHUNK_SIZE`, tighten BM25 (`K1`↓, `B`↑) |
| **Boundary Losses** | Info "cut off" between chunks | ↑ `CHUNK_OVERLAP` |
| **Hallucinations** | Made-up citations, off-base info | ↓ `TEMPERATURE`, enforce citation guardrail in prompt, raise `TOP_K` slightly |
| **Latency High** | Slow query times | ↓ `BM25_TOP_K`, ↓ `VECTOR_TOP_K`, cache embeddings, use smaller model |
| **Short Answers** | Too terse, lacking detail | ↑ `TEMPERATURE` slightly, ↑ `TOP_K` by 1-2, or add "expand" instruction in prompt |
| **Long Docs Dominate** | Verbose docs always rank high | ↑ `BM25_B` (penalize length more) |
| **Keyword Spam** | Repetitive keywords boost irrelevant docs | ↓ `BM25_K1` (reduce TF weight) |

---

### Workflow: Tuning from Scratch

**Step 1: Establish Baseline**
```bash
# Use defaults
make index
make demo
# Observe: What's wrong?
```

**Step 2: Diagnose**
- Missing info → Recall problem
- Irrelevant info → Precision problem
- Boundary issues → Chunking problem
- Hallucinations → Temperature or TOP_K problem

**Step 3: Adjust ONE parameter**
```bash
# Example: Improve recall
TOP_K=6 VECTOR_TOP_K=12 make demo
```

**Step 4: Evaluate**
```bash
make eval
# Check hit-rate@k and avg_score
```

**Step 5: Iterate**

Repeat steps 2-4 until satisfied.

---

### CLI Examples

#### Larger Recall, Same Budget

```bash
TOP_K=6 VECTOR_TOP_K=16 BM25_TOP_K=30 make index
```

#### Precision Mode

```bash
TOP_K=4 CHUNK_SIZE=600 TEMPERATURE=0.1 make run
```

#### Keyword-Heavy Queries

```bash
BM25_TOP_K=35 BM25_K1=1.8 make run
```

#### Fast Inference

```bash
OLLAMA_MODEL=mistral:7b VECTOR_TOP_K=8 BM25_TOP_K=15 make run
```

---

## 6. Parameter Interactions

### Critical Relationships

1. **TOP_K ↔ MAX_CONTEXT_TOKENS**
   ```
   Higher TOP_K → More chunks → Larger context → May exceed MAX_CONTEXT_TOKENS
   Solution: ↑ MAX_CONTEXT_TOKENS or ↓ CHUNK_SIZE
   ```

2. **CHUNK_SIZE ↔ CHUNK_OVERLAP**
   ```
   OVERLAP should be 10-20% of CHUNK_SIZE
   If CHUNK_SIZE=1000, use OVERLAP=150-200
   ```

3. **VECTOR_TOP_K + BM25_TOP_K → TOP_K**
   ```
   Candidate pool should be 2-4x larger than final TOP_K
   If TOP_K=5:
     VECTOR_TOP_K=10-12
     BM25_TOP_K=20-30
   ```

4. **TEMPERATURE ↔ Citation Quality**
   ```
   Higher TEMPERATURE → More creative → May "invent" citations
   Keep TEMPERATURE ≤ 0.3 for RAG to ensure faithful citations
   ```

---

## 7. Example Configurations

### Configuration: Precision-First (Factual Q&A)

```bash
# .env
OLLAMA_MODEL=llama3:8b
TOP_K=4
VECTOR_TOP_K=8
BM25_TOP_K=16
RRF_K=50
CHUNK_SIZE=600
CHUNK_OVERLAP=100
TEMPERATURE=0.1
MAX_CONTEXT_TOKENS=5000
BM25_K1=1.3
BM25_B=0.8
```

**Use Case:** Medical, legal, or scientific Q&A where precision > recall

---

### Configuration: Recall-First (Comprehensive Answers)

```bash
# .env
OLLAMA_MODEL=llama3:8b
TOP_K=8
VECTOR_TOP_K=16
BM25_TOP_K=35
RRF_K=70
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TEMPERATURE=0.3
MAX_CONTEXT_TOKENS=7000
BM25_K1=1.5
BM25_B=0.7
```

**Use Case:** Research, exploratory questions, comprehensive summaries

---

### Configuration: Speed-Optimized

```bash
# .env
OLLAMA_MODEL=mistral:7b
TOP_K=3
VECTOR_TOP_K=6
BM25_TOP_K=12
RRF_K=60
CHUNK_SIZE=500
CHUNK_OVERLAP=80
TEMPERATURE=0.2
MAX_CONTEXT_TOKENS=4000
BM25_K1=1.5
BM25_B=0.75
```

**Use Case:** High-throughput API, real-time chat

---

### Configuration: Keyword-Heavy (Technical Docs)

```bash
# .env
OLLAMA_MODEL=llama3:8b
TOP_K=5
VECTOR_TOP_K=10
BM25_TOP_K=30
RRF_K=60
CHUNK_SIZE=800
CHUNK_OVERLAP=120
TEMPERATURE=0.2
MAX_CONTEXT_TOKENS=6000
BM25_K1=1.8    # ← Higher weight to keyword matches
BM25_B=0.85    # ← Penalize long docs
```

**Use Case:** API docs, code, product specs with exact term matching

---

## Summary Cheatsheet

| Goal | Primary Knobs |
|------|---------------|
| **More facts** | ↑ TOP_K, ↑ VECTOR_TOP_K, ↑ BM25_TOP_K |
| **Less noise** | ↓ TOP_K, ↓ CHUNK_SIZE, ↓ TEMPERATURE |
| **Faster** | ↓ candidates, smaller model, ↓ CHUNK_SIZE |
| **Boundary fixes** | ↑ CHUNK_OVERLAP |
| **Better keywords** | ↑ BM25_TOP_K, ↑ BM25_K1 |
| **Less keyword spam** | ↓ BM25_K1, ↑ BM25_B |

---

**Pro Tip:** Change ONE parameter at a time and run `make eval` to measure impact!

For further reading:
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design
- [EVAL_AND_TUNING.md](EVAL_AND_TUNING.md) - Evaluation workflow
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues


