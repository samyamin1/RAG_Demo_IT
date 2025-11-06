# RAG Kickoff and Run Guide

Complete guide to install, configure, and run the RAG system from scratch.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Indexing Documents](#indexing-documents)
5. [Running the API](#running-the-api)
6. [Running the Demo](#running-the-demo)
7. [Using the API](#using-the-api)
8. [Testing](#testing)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

1. **Python 3.11+**
   ```bash
   python3 --version  # Should be 3.11 or higher
   ```

2. **Ollama**
   
   **macOS / Linux:**
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```
   
   **Windows:**
   Download from https://ollama.com/download/windows
   
   **Verify installation:**
   ```bash
   ollama --version
   ```

3. **Git** (optional, for cloning)
   ```bash
   git --version
   ```

### System Requirements

- **RAM**: 8GB minimum (16GB+ recommended for llama3:8b)
- **Disk**: 10GB free space
- **CPU**: Modern multi-core processor
- **GPU**: Optional (CUDA/Metal for faster inference)

---

## Installation

### Option 1: One-Command Bootstrap (Recommended)

```bash
# Navigate to project directory
cd RAG

# Run bootstrap script
bash scripts/bootstrap.sh
```

The bootstrap script will:
1. ✅ Check Python version
2. ✅ Create virtual environment
3. ✅ Install dependencies
4. ✅ Check/install Ollama
5. ✅ Pull the llama3:8b model
6. ✅ Prepare dataset
7. ✅ Create .env file
8. ✅ Build indices

**This is the fastest way to get started!**

### Option 2: Manual Step-by-Step

#### 1. Create Virtual Environment

```bash
python3 -m venv .venv
```

#### 2. Activate Virtual Environment

**Linux/macOS:**
```bash
source .venv/bin/activate
```

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
.venv\Scripts\activate.bat
```

#### 3. Upgrade pip

```bash
pip install --upgrade pip
```

#### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `langchain` - LLM framework
- `chromadb` - Vector store
- `rank-bm25` - Lexical search
- `ollama` - Ollama client
- `pydantic` - Data validation
- And more...

#### 5. Install and Pull Ollama Model

```bash
# Verify Ollama is installed
ollama list

# Pull the default model (llama3:8b - ~4.7GB download)
ollama pull llama3:8b
```

**Alternative models:**
```bash
# Smaller model (faster, less capable)
ollama pull llama3.1:8b

# Larger model (slower, more capable)
ollama pull llama3:70b  # Requires 64GB+ RAM!
```

#### 6. Prepare Dataset

```bash
# Ensure rag_sample_qas_from_kis.csv is in project root
python scripts/fetch_kaggle_dataset.py
```

The dataset should be placed at: `data/raw/rag_sample_qas_from_kis.csv`

---

## Configuration

### Create .env File

If not already created by bootstrap, create `.env` in project root:

```bash
# Copy from example
cp .env.example .env
```

### Key Configuration Parameters

Edit `.env` to customize:

```bash
# Ollama Configuration
OLLAMA_MODEL=llama3:8b              # Model to use
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_EMBED_MODEL=nomic-embed-text

# Retrieval Parameters
TOP_K=5                             # Final results after fusion
VECTOR_TOP_K=10                     # Vector candidates
BM25_TOP_K=20                       # BM25 candidates
RRF_K=60                            # RRF fusion parameter

# Chunking
CHUNK_SIZE=800                      # Tokens per chunk
CHUNK_OVERLAP=120                   # Overlap between chunks

# LLM Generation
TEMPERATURE=0.2                     # Lower = more deterministic
MAX_CONTEXT_TOKENS=6000             # Context window budget
```

**See [PARAMETERS.md](PARAMETERS.md) for detailed tuning guide!**

---

## Indexing Documents

### Build Indices from Scratch

```bash
# Using Makefile
make index

# Or directly
python scripts/index_documents.py --rebuild
```

This will:
1. Load CSV dataset
2. Parse documents into chunks
3. Generate embeddings (via Ollama)
4. Build ChromaDB vector index
5. Build BM25 lexical index

**Indexing Options:**

```bash
# Index specific CSV
python scripts/index_documents.py --csv data/my_dataset.csv

# Limit number of documents (for testing)
python scripts/index_documents.py --limit 100

# Force rebuild (wipe existing indices)
python scripts/index_documents.py --rebuild
```

### Verify Indexing

After indexing, you should see:

```
====================================================================
INDEXING COMPLETE
====================================================================
Documents indexed:   250
Total chunks:        1543
Vector store count:  1543
BM25 store count:    1543
====================================================================
```

---

## Running the API

### Start the FastAPI Server

```bash
# Using Makefile
make run

# Or directly
uvicorn rag.api.rag:app --reload --host 0.0.0.0 --port 8000
```

You should see:

```
====================================================================
RAG SYSTEM CONFIGURATION
====================================================================
Ollama Model:        llama3:8b
Ollama URL:          http://localhost:11434
...
====================================================================

INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Access API Documentation

Open in browser:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## Running the Demo

### Wrong→Right Demonstration

```bash
# Using Makefile
make demo

# Or directly
python scripts/demo_wrong_right.py
```

This demo shows:

1. **❌ WITHOUT RAG**: LLM answer with no context (may hallucinate)
2. **✅ WITH RAG**: LLM answer with retrieved context + citations

**Example Output:**

```
======================================================================
DEMO 1: What are the main benefits of retrieval augmented generation?
======================================================================

----------------------------------------------------------------------
❌ WITHOUT RAG (Baseline - May Hallucinate)
----------------------------------------------------------------------

Answer:
Retrieval augmented generation (RAG) offers several benefits...
[Generic answer based on training data]

⚠ Note: This answer may be outdated, incorrect, or hallucinated.

----------------------------------------------------------------------
✅ WITH RAG (Retrieval + Context)
----------------------------------------------------------------------

Answer:
According to [doc_023.csv], retrieval augmented generation combines
retrieval with LLMs to improve accuracy by grounding responses in
specific knowledge bases. [doc_045.csv] notes that RAG reduces
hallucinations by citing sources...

📚 Sources (5):
  1. doc_023.csv (score: 0.847, route: hybrid)
  2. doc_045.csv (score: 0.792, route: hybrid)
  3. doc_089.csv (score: 0.731, route: vector)
  4. doc_012.csv (score: 0.684, route: bm25)
  5. doc_134.csv (score: 0.657, route: hybrid)

✓ This answer is grounded in the knowledge base with citations.
```

---

## Using the API

### Upload a Document

```bash
curl -X POST "http://localhost:8000/upload" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Retrieval augmented generation (RAG) combines retrieval with LLMs to improve answer accuracy by grounding responses in a knowledge base.",
    "filename": "rag_intro.txt"
  }'
```

**Response:**
```json
{
  "doc_id": "a7f3c2d1-...",
  "filename": "rag_intro.txt",
  "chunks_created": 1,
  "status": "success"
}
```

### Query with RAG

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is RAG?",
    "top_k": 5
  }'
```

**Response:**
```json
{
  "answer": "According to [rag_intro.txt], RAG combines retrieval with LLMs...",
  "sources": [
    {
      "id": "a7f3c2d1-..._chunk_0",
      "filename": "rag_intro.txt",
      "score": 0.867,
      "route": "hybrid"
    }
  ],
  "query": "What is RAG?"
}
```

### Delete a Document

```bash
curl -X DELETE "http://localhost:8000/delete?doc_id=a7f3c2d1-..."
```

### Check System Status

```bash
curl http://localhost:8000/status
```

**Response:**
```json
{
  "status": "ok",
  "ollama_available": true,
  "ollama_model": "llama3:8b",
  "indices_loaded": true,
  "vector_chunks": 1543,
  "bm25_chunks": 1543
}
```

---

## Testing

### Run All Tests

```bash
# Using Makefile
make test

# Or directly
pytest -v
```

### Run Specific Tests

```bash
# Test RRF fusion
pytest tests/test_rrf.py -v

# Test retrieval
pytest tests/test_retrieval.py -v

# Test API endpoints
pytest tests/test_api.py -v
```

### Run Evaluation

```bash
# Parameter grid search
make eval

# Or directly
python scripts/eval_grid.py
```

---

## Troubleshooting

### Common Issues

#### 1. Ollama Not Found

**Error:** `ollama: command not found`

**Solution:**
```bash
# macOS/Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# Download from https://ollama.com/download/windows
```

#### 2. Model Not Pulled

**Error:** `Model llama3:8b not found`

**Solution:**
```bash
ollama pull llama3:8b
```

#### 3. Ollama Not Running

**Error:** `Connection refused to localhost:11434`

**Solution:**
```bash
# Start Ollama service
ollama serve

# Or on macOS, ensure Ollama app is running
```

#### 4. No Documents Indexed

**Error:** `indices_loaded: false`

**Solution:**
```bash
python scripts/index_documents.py --rebuild
```

#### 5. Port Already in Use

**Error:** `Address already in use: 8000`

**Solution:**
```bash
# Use different port
uvicorn rag.api.rag:app --port 8080
```

#### 6. ChromaDB Lock Error

**Error:** `Database is locked`

**Solution:**
```bash
# Stop all processes using ChromaDB
# Remove lock files
rm -rf .chroma/*.lock

# Rebuild indices
python scripts/index_documents.py --rebuild
```

### Getting Help

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for more detailed solutions.

---

## Next Steps

1. ✅ **Tune Parameters**: Read [PARAMETERS.md](PARAMETERS.md)
2. ✅ **Understand Architecture**: Read [ARCHITECTURE.md](ARCHITECTURE.md)
3. ✅ **Run Evaluation**: `make eval`
4. ✅ **Integrate with Your App**: Use the Python API or REST endpoints

---

## Summary Commands

```bash
# Quick Start (all-in-one)
bash scripts/bootstrap.sh && make demo

# Or step-by-step
make setup        # Install dependencies
make ollama       # Pull model
make data         # Prepare dataset
make index        # Build indices
make run          # Start API
make demo         # Run demo
make test         # Run tests
```

**Happy RAGing! 🚀**


