# Quick Start Guide

Get RAG running in 5 minutes!

## Prerequisites

- Python 3.11+
- 8GB+ RAM
- Ollama installed ([get it here](https://ollama.com/download))

## Installation

### Option 1: One Command (Recommended)

```bash
bash scripts/bootstrap.sh
```

This will:
1. Create virtual environment
2. Install dependencies
3. Pull Ollama model
4. Index documents
5. Configure everything

### Option 2: Manual

```bash
# 1. Setup
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Pull Ollama model
ollama pull llama3:8b

# 3. Index documents
python scripts/index_documents.py --rebuild
```

## Verify Setup

```bash
python scripts/verify_setup.py
```

Should see all checks ✓

## Run Demo

```bash
make demo
```

This shows "Wrong→Right" comparison:
- ❌ LLM without RAG (may hallucinate)
- ✅ LLM with RAG (cites sources)

## Start API

```bash
make run
```

Visit http://localhost:8000/docs for interactive API

## Try It

```bash
# Query via API
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is RAG?", "top_k": 5}'
```

Or use Python:

```python
from rag.core.service import CentralizedRAGService

rag = CentralizedRAGService()
response = rag.query_with_answer("What is RAG?")
print(response.answer)
for src in response.sources:
    print(f"  - {src.filename} ({src.score:.3f})")
```

## Next Steps

- 📖 Read [RAG_Kickoff_and_Run.md](RAG_Kickoff_and_Run.md) for full guide
- ⚙️ Tune parameters: [PARAMETERS.md](PARAMETERS.md)
- 🏗️ Understand architecture: [ARCHITECTURE.md](ARCHITECTURE.md)
- 🐛 Troubleshoot: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## Common Commands

```bash
make setup    # Install dependencies
make ollama   # Check Ollama & pull model
make index    # Build indices
make run      # Start API
make demo     # Run wrong→right demo
make test     # Run tests
make clean    # Clean indices
```

## Help

Something not working?

1. Run: `python scripts/verify_setup.py`
2. Check: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
3. Re-run: `bash scripts/bootstrap.sh`

---

**Ready in 5 minutes! 🚀**


