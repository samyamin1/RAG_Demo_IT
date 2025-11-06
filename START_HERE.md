# 🚀 START HERE - RAG Module Navigation

Welcome to the RAG Module! This guide helps you find exactly what you need.

---

## ⚡ I Want To...

### Get Started (5 minutes)

**→ [QUICK_START.md](QUICK_START.md)**

```bash
bash scripts/bootstrap.sh && make demo
```

---

### Understand What This Is

**→ [README.md](README.md)** - Project overview, features, examples

**Key Points:**
- Fully local RAG with Ollama
- Hybrid retrieval (vector + BM25 + RRF fusion)
- Citation-based answers
- FastAPI REST API

---

### Install & Configure

**→ [RAG_Kickoff_and_Run.md](RAG_Kickoff_and_Run.md)** - Complete setup guide

**Topics:**
- Prerequisites
- Installation (bootstrap + manual)
- Configuration (.env)
- Indexing documents
- Running API
- Using the demo
- Testing

---

### Make RAG Work Better ⭐

**→ [PARAMETERS.md](PARAMETERS.md)** - **ESSENTIAL TUNING GUIDE**

**Covers:**
- All 28 parameters explained
- What/Why/How for each setting
- Tuning strategies
- Problem-solution matrix
- Example configurations
- CLI examples

**Common Problems → Solutions:**
```
Missing facts?    → ↑ TOP_K, ↑ VECTOR_TOP_K
Noisy answers?    → ↓ TOP_K, ↓ CHUNK_SIZE
Slow queries?     → ↓ candidates, smaller model
Hallucinations?   → ↓ TEMPERATURE
Boundary losses?  → ↑ CHUNK_OVERLAP
```

---

### Fix Problems

**→ [TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues & solutions

**Categories:**
- Installation issues
- Ollama issues
- Indexing issues
- Query issues
- Performance issues
- API issues
- Configuration issues

**Quick Recovery:**
```bash
make clean
bash scripts/bootstrap.sh
```

---

### Understand How It Works

**→ [ARCHITECTURE.md](ARCHITECTURE.md)** - Detailed system architecture

**Covers:**
- Component breakdown
- Data flow diagrams
- Sequence diagrams
- Storage structure
- Extension points
- Performance considerations

**Key Components:**
1. CentralizedRAGService (orchestration)
2. DocumentIngestionService (parse → chunk → embed)
3. DocumentRetrievalService (hybrid search)
4. ContextAssembler (prompt builder)
5. LocalLLMWrapper (Ollama)
6. FastAPI (REST API)

---

### Evaluate & Improve

**→ [EVAL_AND_TUNING.md](EVAL_AND_TUNING.md)** - Systematic improvement

**Topics:**
- Running evaluations
- Metrics (hit rate, avg score)
- Grid search
- A/B testing
- Continuous improvement

```bash
make eval  # Run parameter grid search
```

---

### Contribute or Extend

**→ [CONTRIBUTING.md](CONTRIBUTING.md)** - Development guidelines

**Topics:**
- Setting up dev environment
- Code style
- Adding features
- Testing
- Pull request process

---

### Navigate the Code

**→ [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - File organization

**Quick Reference:**
```
rag/api/rag.py              → FastAPI endpoints
rag/core/service.py         → Main orchestration
rag/retrieval/hybrid.py     → Hybrid search
rag/llm/ollama_wrapper.py   → Ollama integration
scripts/demo_wrong_right.py → Demo script
```

---

## 📋 Quick Reference

### Commands

```bash
# Setup
bash scripts/bootstrap.sh      # One-command setup
make setup                     # Manual setup

# Verify
python scripts/verify_setup.py # Check everything

# Data
make data                      # Prepare dataset
make index                     # Build indices

# Run
make run                       # Start API
make demo                      # Run wrong→right demo

# Test
make test                      # Run tests
make eval                      # Parameter evaluation

# Clean
make clean                     # Remove indices
```

---

### Files at a Glance

| File | Purpose |
|------|---------|
| **START_HERE.md** | This file - navigation guide |
| **QUICK_START.md** | 5-minute quickstart |
| **README.md** | Project overview |
| **RAG_Kickoff_and_Run.md** | Complete setup guide |
| **PARAMETERS.md** ⭐ | **Tuning guide (ESSENTIAL)** |
| **ARCHITECTURE.md** | System design |
| **TROUBLESHOOTING.md** | Problem solving |
| **EVAL_AND_TUNING.md** | Evaluation guide |
| **CONTRIBUTING.md** | Development guide |
| **PROJECT_STRUCTURE.md** | File organization |
| **DELIVERY_SUMMARY.md** | What was delivered |

---

### Configuration Quick Reference

```bash
# In .env or environment variables

# Retrieval
TOP_K=5                    # Final results
VECTOR_TOP_K=10           # Vector candidates
BM25_TOP_K=20             # BM25 candidates
RRF_K=60                  # Fusion parameter

# Chunking
CHUNK_SIZE=800            # Tokens per chunk
CHUNK_OVERLAP=120         # Overlap tokens

# LLM
OLLAMA_MODEL=llama3:8b    # Model name
TEMPERATURE=0.2           # Sampling temp
MAX_CONTEXT_TOKENS=6000   # Context budget

# BM25
BM25_K1=1.5               # TF saturation
BM25_B=0.75               # Length normalization
```

**See [PARAMETERS.md](PARAMETERS.md) for complete reference!**

---

### API Quick Reference

**Endpoints:**

```bash
# Health
curl http://localhost:8000/health

# Upload
curl -X POST http://localhost:8000/upload \
  -H "Content-Type: application/json" \
  -d '{"content": "RAG text", "filename": "doc.txt"}'

# Query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is RAG?", "top_k": 5}'

# Delete
curl -X DELETE "http://localhost:8000/delete?doc_id=123"

# Docs
http://localhost:8000/docs  # Swagger UI
```

---

### Python Quick Reference

```python
from rag.core.service import CentralizedRAGService

# Initialize
rag = CentralizedRAGService()

# Upload
result = rag.upload_document(
    content="RAG combines retrieval with LLMs.",
    filename="intro.txt"
)

# Query
response = rag.query_with_answer("What is RAG?")
print(response.answer)

# View sources
for src in response.sources:
    print(f"[{src.filename}] score={src.score:.3f} route={src.route}")
```

---

## 🎯 Common Workflows

### First Time Setup

1. **[QUICK_START.md](QUICK_START.md)** - Get running
2. **[RAG_Kickoff_and_Run.md](RAG_Kickoff_and_Run.md)** - Understand setup
3. **Run demo** - `make demo`
4. **Explore API** - http://localhost:8000/docs

### Improving Performance

1. **[PARAMETERS.md](PARAMETERS.md)** - Learn tuning
2. **Run baseline** - `make demo`
3. **Adjust parameters** - Edit `.env`
4. **Evaluate** - `make eval`
5. **Iterate**

### Development

1. **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Navigate code
2. **[ARCHITECTURE.md](ARCHITECTURE.md)** - Understand design
3. **[CONTRIBUTING.md](CONTRIBUTING.md)** - Development guide
4. **Write tests** - `tests/test_*.py`
5. **Submit PR**

### Troubleshooting

1. **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Find your issue
2. **Run verification** - `python scripts/verify_setup.py`
3. **Check logs** - Terminal where API runs
4. **Clean start** - `make clean && bash scripts/bootstrap.sh`

---

## 💡 Tips

### For Best Results

1. **Read PARAMETERS.md** - Tuning makes a huge difference
2. **Start with defaults** - Establish baseline before tuning
3. **Change one parameter at a time** - Isolate effects
4. **Run eval** - Measure impact of changes
5. **Monitor performance** - Track latency and quality

### Common Mistakes to Avoid

❌ Changing multiple parameters at once
❌ Not running `make index` after changing chunk size
❌ Using too high temperature (causes hallucinations)
❌ Not checking Ollama is running
❌ Ignoring the documentation

✅ Read docs first
✅ Verify setup with `verify_setup.py`
✅ Use `make demo` to test changes
✅ Run `make eval` for systematic tuning
✅ Keep temperature ≤ 0.3 for factual RAG

---

## 🏆 Success Criteria

You'll know it's working when:

1. ✅ `make demo` shows cited answers (not hallucinations)
2. ✅ API returns `{"status": "ok", "indices_loaded": true}`
3. ✅ Sources include relevant documents with high scores
4. ✅ Answers reference [filenames] in square brackets
5. ✅ All tests pass (`make test`)

---

## 📞 Getting Help

**Stuck?** Follow this order:

1. **[QUICK_START.md](QUICK_START.md)** - Basics
2. **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Known issues
3. **`python scripts/verify_setup.py`** - Diagnosis
4. **[RAG_Kickoff_and_Run.md](RAG_Kickoff_and_Run.md)** - Detailed setup
5. **Clean slate:** `make clean && bash scripts/bootstrap.sh`

---

## 🎓 Learning Path

**Beginner:**
1. QUICK_START.md → Get it running
2. README.md → Understand what it does
3. Run `make demo` → See it in action

**Intermediate:**
4. RAG_Kickoff_and_Run.md → Deep setup knowledge
5. PARAMETERS.md ⭐ → Tune for your use case
6. TROUBLESHOOTING.md → Handle issues

**Advanced:**
7. ARCHITECTURE.md → Understand internals
8. EVAL_AND_TUNING.md → Systematic optimization
9. CONTRIBUTING.md → Extend the system

---

## ✨ Key Highlights

- **🚀 5-minute setup** with `bash scripts/bootstrap.sh`
- **🎯 Production-ready** with tests and docs
- **🔧 Fully configurable** with 28+ parameters
- **📚 3,300+ lines** of comprehensive documentation
- **🏗️ Modular architecture** - easy to extend
- **🔍 Hybrid retrieval** - vector + BM25 + RRF
- **💯 Citation-based** - no hallucinations
- **🌐 REST API** - easy integration
- **🧪 Evaluation tools** - systematic improvement

---

**Ready to start?** → [QUICK_START.md](QUICK_START.md)

**Need to tune?** → [PARAMETERS.md](PARAMETERS.md) ⭐

**Having issues?** → [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

**Have fun RAGing! 🎉**


