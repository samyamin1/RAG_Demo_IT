# Troubleshooting Guide

Common issues and solutions for the RAG system.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Ollama Issues](#ollama-issues)
3. [Indexing Issues](#indexing-issues)
4. [Query Issues](#query-issues)
5. [Performance Issues](#performance-issues)
6. [API Issues](#api-issues)
7. [Configuration Issues](#configuration-issues)

---

## Installation Issues

### Python Version Too Old

**Error:**
```
SyntaxError: invalid syntax
```
or
```
RuntimeError: Python 3.11+ required
```

**Solution:**
```bash
# Check version
python3 --version

# Install Python 3.11+ (Ubuntu/Debian)
sudo apt update
sudo apt install python3.11 python3.11-venv

# macOS
brew install python@3.11

# Windows
# Download from https://www.python.org/downloads/
```

---

### pip install Failures

**Error:**
```
ERROR: Could not build wheels for XXX
```

**Solution:**
```bash
# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install build tools (Ubuntu/Debian)
sudo apt install python3-dev build-essential

# macOS
xcode-select --install

# Windows
# Install Visual Studio Build Tools
```

---

### Virtual Environment Issues

**Error:**
```
No module named 'venv'
```

**Solution:**
```bash
# Ubuntu/Debian
sudo apt install python3.11-venv

# Then retry
python3.11 -m venv .venv
```

---

## Ollama Issues

### Ollama Not Found

**Error:**
```
ollama: command not found
```

**Solution:**

**macOS/Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
1. Download from https://ollama.com/download/windows
2. Run installer
3. Restart terminal

**Verify:**
```bash
ollama --version
```

---

### Ollama Not Running

**Error:**
```
ConnectionRefusedError: Connection refused to localhost:11434
```

**Solution:**

**Option 1: Start Ollama service**
```bash
ollama serve
```

**Option 2: Check if already running**
```bash
# macOS/Linux
ps aux | grep ollama

# Windows
tasklist | findstr ollama
```

**Option 3: Check Ollama app (macOS)**
- Ensure Ollama app is running in menu bar
- Restart Ollama app

**Option 4: Change port**
```bash
# In .env
OLLAMA_BASE_URL=http://localhost:11434
```

---

### Model Not Found

**Error:**
```
Error: model 'llama3:8b' not found
```

**Solution:**
```bash
# Pull the model
ollama pull llama3:8b

# Verify
ollama list

# Should see:
# NAME            SIZE
# llama3:8b       4.7GB
```

---

### Out of Memory (OOM)

**Error:**
```
Killed
```
or
```
RuntimeError: CUDA out of memory
```

**Solution:**

**Option 1: Use smaller model**
```bash
# In .env
OLLAMA_MODEL=mistral:7b  # Instead of llama3:8b
```

**Option 2: Reduce concurrent requests**
```bash
# Don't run multiple queries simultaneously
```

**Option 3: Increase swap (Linux)**
```bash
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

**Option 4: Use quantized model**
```bash
ollama pull llama3:8b-q4_0  # 4-bit quantization
```

---

### Slow Inference

**Symptoms:** Queries take 10+ seconds per response

**Solutions:**

1. **Enable GPU acceleration**
   ```bash
   # Check CUDA/Metal availability
   ollama ps
   
   # Should show GPU utilization
   ```

2. **Use smaller model**
   ```bash
   OLLAMA_MODEL=mistral:7b
   ```

3. **Reduce output length**
   ```bash
   # In .env
   MAX_OUTPUT_TOKENS=512
   ```

4. **Reduce context**
   ```bash
   TOP_K=3
   MAX_CONTEXT_TOKENS=4000
   ```

---

## Indexing Issues

### Dataset Not Found

**Error:**
```
FileNotFoundError: rag_sample_qas_from_kis.csv not found
```

**Solution:**
```bash
# Ensure CSV is in project root or data/raw/
python scripts/fetch_kaggle_dataset.py

# Or manually place file
cp /path/to/rag_sample_qas_from_kis.csv data/raw/
```

---

### ChromaDB Lock Error

**Error:**
```
sqlite3.OperationalError: database is locked
```

**Solution:**
```bash
# Stop all processes using ChromaDB
# Remove lock files
rm -rf .chroma/*.lock

# Rebuild indices
python scripts/index_documents.py --rebuild
```

---

### BM25 Pickle Error

**Error:**
```
pickle.UnpicklingError: invalid load key
```

**Solution:**
```bash
# Remove corrupted BM25 index
rm -rf .bm25/

# Rebuild
python scripts/index_documents.py --rebuild
```

---

### Embedding Failures

**Error:**
```
RuntimeError: Embedding failed for text: ...
```

**Solutions:**

1. **Check Ollama is running**
   ```bash
   ollama serve
   ```

2. **Pull embedding model**
   ```bash
   ollama pull nomic-embed-text
   ```

3. **Try alternative model**
   ```bash
   # In .env
   OLLAMA_EMBED_MODEL=llama3:8b
   ```

---

### Index Count Mismatch

**Symptoms:** `vector_chunks: 1543, bm25_chunks: 1520` (different counts)

**Solution:**
```bash
# Full rebuild
python scripts/wipe_indices.py
python scripts/index_documents.py --rebuild
```

---

## Query Issues

### No Results Returned

**Symptoms:** `sources: []` in response

**Diagnosis:**
```bash
# Check index counts
curl http://localhost:8000/status

# Should show:
# "vector_chunks": 1543,
# "bm25_chunks": 1543
```

**Solutions:**

1. **Rebuild indices**
   ```bash
   make index
   ```

2. **Increase TOP_K**
   ```bash
   TOP_K=10 make demo
   ```

3. **Check query embedding**
   - Query may be too different from indexed content
   - Try more specific queries

---

### Hallucinated Answers

**Symptoms:** Answer cites non-existent documents or makes up facts

**Solutions:**

1. **Lower temperature**
   ```bash
   # In .env
   TEMPERATURE=0.1
   ```

2. **Increase TOP_K** (more grounding)
   ```bash
   TOP_K=6
   ```

3. **Strengthen system prompt**
   - Edit `rag/prompts/system.py`
   - Add stricter citation rules

---

### Wrong Documents Retrieved

**Symptoms:** Retrieved chunks don't match query intent

**Solutions:**

1. **Tune retrieval parameters**
   ```bash
   # Favor vector search
   VECTOR_TOP_K=15
   BM25_TOP_K=10
   
   # Or favor BM25
   VECTOR_TOP_K=8
   BM25_TOP_K=30
   ```

2. **Adjust RRF_K**
   ```bash
   RRF_K=50  # More aggressive fusion
   ```

3. **Change chunk size**
   ```bash
   CHUNK_SIZE=600  # Smaller, more precise
   ```

---

### Context Window Exceeded

**Error:**
```
Error: context window exceeded
```

**Solutions:**

1. **Reduce TOP_K**
   ```bash
   TOP_K=3
   ```

2. **Reduce MAX_CONTEXT_TOKENS**
   ```bash
   MAX_CONTEXT_TOKENS=4000
   ```

3. **Smaller chunks**
   ```bash
   CHUNK_SIZE=600
   ```

---

## Performance Issues

### Slow Queries (>10s)

**Diagnosis:**
```bash
# Check where time is spent
# Add logging to rag/core/service.py
```

**Solutions by Bottleneck:**

| Bottleneck | Solution |
|------------|----------|
| **Embedding** | Cache query embeddings, use faster model |
| **Vector search** | Reduce `VECTOR_TOP_K`, optimize ChromaDB |
| **BM25 search** | Reduce corpus size, reduce `BM25_TOP_K` |
| **LLM generation** | Use smaller model, reduce output length |

**Quick wins:**
```bash
# Reduce candidate counts
VECTOR_TOP_K=8
BM25_TOP_K=15

# Use faster model
OLLAMA_MODEL=mistral:7b

# Limit output
MAX_OUTPUT_TOKENS=512
```

---

### High Memory Usage

**Symptoms:** System using 16GB+ RAM

**Solutions:**

1. **Smaller model**
   ```bash
   ollama pull mistral:7b
   OLLAMA_MODEL=mistral:7b
   ```

2. **Reduce batch size** (if indexing)
   ```bash
   python scripts/index_documents.py --limit 100
   ```

3. **Clear indices when not in use**
   ```bash
   make clean
   ```

---

### Disk Space Issues

**Error:**
```
OSError: [Errno 28] No space left on device
```

**Solutions:**

1. **Check disk usage**
   ```bash
   du -sh .chroma .bm25
   ollama list
   ```

2. **Remove unused models**
   ```bash
   ollama rm llama3:70b
   ```

3. **Compress indices** (if supported)

---

## API Issues

### Port Already in Use

**Error:**
```
OSError: [Errno 48] Address already in use
```

**Solutions:**

1. **Use different port**
   ```bash
   uvicorn rag.api.rag:app --port 8080
   ```

2. **Kill existing process**
   ```bash
   # Find process on port 8000
   lsof -i :8000  # macOS/Linux
   
   # Kill it
   kill -9 <PID>
   ```

   ```powershell
   # Windows
   netstat -ano | findstr :8000
   taskkill /PID <PID> /F
   ```

---

### 422 Validation Error

**Error:**
```json
{
  "detail": [
    {
      "loc": ["body", "query"],
      "msg": "field required"
    }
  ]
}
```

**Solution:**
Check request payload matches Pydantic models:

```bash
# Correct
curl -X POST "/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is RAG?"}'

# Incorrect (missing "query" field)
curl -X POST "/query" \
  -H "Content-Type: application/json" \
  -d '{"q": "What is RAG?"}'
```

---

### 500 Internal Server Error

**Symptoms:** API returns 500, check server logs

**Common Causes:**

1. **Ollama not running**
   ```bash
   ollama serve
   ```

2. **Indices not built**
   ```bash
   make index
   ```

3. **Config error**
   - Check `.env` file syntax
   - No quotes around values

---

## Configuration Issues

### .env Not Loading

**Symptoms:** Default values used instead of .env

**Solutions:**

1. **Check file location**
   ```bash
   ls -la .env  # Should be in project root
   ```

2. **Check file format**
   ```bash
   # .env should have no quotes
   TOP_K=5          # ✓ Correct
   TOP_K="5"        # ✗ Wrong (will be string)
   ```

3. **Restart service**
   ```bash
   # .env is loaded at startup
   make run
   ```

---

### Environment Variable Override Not Working

**Issue:** Setting `TOP_K=6 make demo` doesn't change behavior

**Solution:**

```bash
# Ensure variable is exported
export TOP_K=6
make demo

# Or inline (works with most shells)
TOP_K=6 python scripts/demo_wrong_right.py
```

---

### Wrong Model Used

**Symptoms:** Different model than expected

**Diagnosis:**
```bash
curl http://localhost:8000/status
# Check "ollama_model" field
```

**Solution:**
```bash
# Update .env
OLLAMA_MODEL=llama3:8b

# Pull model
ollama pull llama3:8b

# Restart API
make run
```

---

## Debugging Tips

### Enable Verbose Logging

Add to `rag/config.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check System Status

```bash
# Via API
curl http://localhost:8000/status

# Via Python
python -c "from rag.core.service import CentralizedRAGService; print(CentralizedRAGService().get_status())"
```

### Inspect Indices

```python
from rag.retrieval.hybrid import DocumentRetrievalService

service = DocumentRetrievalService()
print(service.count())  # {'vector': 1543, 'bm25': 1543}

# Test retrieval
results = service.query_documents("test query", top_k=3)
for r in results:
    print(f"{r.filename}: {r.score:.3f} ({r.route})")
```

### Test Individual Components

```bash
# Test Ollama
python -c "from rag.llm.ollama_wrapper import LocalLLMWrapper; print(LocalLLMWrapper().check_available())"

# Test embeddings
python -c "from rag.llm.ollama_wrapper import OllamaEmbeddings; print(len(OllamaEmbeddings().embed_query('test')))"

# Test vector store
python -c "from rag.retrieval.chroma import ChromaVectorStore; print(ChromaVectorStore().count())"
```

---

## Getting Help

If issues persist:

1. **Check logs** in terminal where API is running
2. **Review configuration** with `python -c "from rag.config import print_config; print_config()"`
3. **Run tests** with `make test` to isolate component issues
4. **Rebuild from scratch** with `bash scripts/bootstrap.sh`

**Still stuck?** 
- Review [RAG_Kickoff_and_Run.md](RAG_Kickoff_and_Run.md)
- Check [PARAMETERS.md](PARAMETERS.md) for tuning
- Consult [ARCHITECTURE.md](ARCHITECTURE.md) for system design

---

## Quick Recovery Checklist

When everything breaks:

```bash
# 1. Stop all processes
pkill -f uvicorn
pkill -f ollama

# 2. Clean state
make clean
rm -rf .venv

# 3. Fresh start
bash scripts/bootstrap.sh

# 4. Verify
make demo
```

This should resolve 90% of issues!


