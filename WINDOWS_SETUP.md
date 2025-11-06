# Windows Setup Guide for RAG System

Complete step-by-step guide for Windows 10/11.

## Step 1: Install Python 3.11+

### Download and Install

1. **Go to**: https://www.python.org/downloads/
2. **Download**: Python 3.11 or later (get the "Windows installer (64-bit)")
3. **Run installer** and **IMPORTANT**:
   - ✅ Check "Add python.exe to PATH"
   - ✅ Check "Install pip"
   - Click "Install Now"

4. **Verify installation**:
   Open new PowerShell or Command Prompt:
   ```powershell
   python --version
   # Should show: Python 3.11.x or higher
   ```

**Alternative - Using Chocolatey:**
```powershell
# If you have Chocolatey package manager
choco install python311
```

**Alternative - Using winget:**
```powershell
# Windows 10 (version 1809+) and Windows 11
winget install Python.Python.3.11
```

---

## Step 2: Install Ollama

### Download Ollama

1. **Go to**: https://ollama.com/download/windows
2. **Download**: OllamaSetup.exe
3. **Run installer**: Follow the prompts
4. **Ollama will start automatically** (you'll see it in your system tray)

### Verify Ollama

Open PowerShell:
```powershell
ollama --version
# Should show: ollama version is ...
```

### Pull the Model

```powershell
# Pull llama3:8b (default model - 4.7GB download)
ollama pull llama3:8b

# Wait for download to complete
# Verify:
ollama list
```

**Note:** You need at least 8GB RAM for llama3:8b. If you have less, use a smaller model:
```powershell
ollama pull mistral:7b  # Smaller alternative
```

---

## Step 3: Setup RAG Project

### Navigate to Project

Open PowerShell and navigate to project directory:
```powershell
cd "C:\Users\smami\Downloads\AI Consultations\InnovaDigits\RAG"
```

### Create Virtual Environment

```powershell
# Create virtual environment
python -m venv .venv

# Activate it
.\.venv\Scripts\Activate.ps1
```

**If you get execution policy error:**
```powershell
# Run this first (as Administrator):
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then retry activation:
.\.venv\Scripts\Activate.ps1
```

Your prompt should now show `(.venv)` at the start.

### Install Dependencies

```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

This will take a few minutes to download and install all packages.

---

## Step 4: Prepare Dataset

The CSV file `rag_sample_qas_from_kis.csv` should already be in your project root.

**Verify:**
```powershell
dir rag_sample_qas_from_kis.csv
```

If not found, make sure it's in the project directory.

**Run preparation script:**
```powershell
python scripts/fetch_kaggle_dataset.py
```

---

## Step 5: Configure Environment

### Create .env File

Copy the example configuration:
```powershell
Copy-Item env.example .env
```

### Edit .env (Optional)

Open `.env` in notepad or your favorite editor:
```powershell
notepad .env
```

**For machines with limited RAM (8-16GB):**
```bash
# Change to smaller model
OLLAMA_MODEL=mistral:7b

# Reduce candidates
VECTOR_TOP_K=8
BM25_TOP_K=15
TOP_K=4

# Smaller chunks
CHUNK_SIZE=600
MAX_CONTEXT_TOKENS=4000
```

**For powerful machines (32GB+ RAM):**
```bash
# Keep defaults or increase
OLLAMA_MODEL=llama3:8b
VECTOR_TOP_K=12
BM25_TOP_K=25
TOP_K=6
CHUNK_SIZE=1000
MAX_CONTEXT_TOKENS=7000
```

---

## Step 6: Build Indices

```powershell
# Index the documents (this will take 5-10 minutes)
python scripts/index_documents.py --rebuild
```

**You should see:**
```
====================================================================
INDEXING COMPLETE
====================================================================
Documents indexed:   [number]
Total chunks:        [number]
Vector store count:  [number]
BM25 store count:    [number]
====================================================================
```

---

## Step 7: Run the Demo

### Quick Test - Wrong vs Right Demo

```powershell
python scripts/demo_wrong_right.py
```

**Expected output:**
- Configuration display
- Demo Question 1:
  - ❌ WITHOUT RAG (may be generic/wrong)
  - ✅ WITH RAG (with citations)
- Demo Question 2:
  - Same format

### Better Use Case Demo (Clear Differences)

```powershell
python scripts/demo_medical_usecase.py
```

This will show medical/technical questions where RAG makes a HUGE difference.

---

## Step 8: Start the API

```powershell
# Start FastAPI server
python -m uvicorn rag.api.rag:app --reload --host 127.0.0.1 --port 8000
```

**You should see:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Open in browser:**
- **API Docs**: http://127.0.0.1:8000/docs
- **Health Check**: http://127.0.0.1:8000/health

**Keep this PowerShell window open** while the API runs.

---

## Step 9: Test the API

Open a **NEW PowerShell window** and run:

```powershell
# Test health
curl http://127.0.0.1:8000/health

# Query (using Invoke-WebRequest)
$body = @{
    query = "What are the benefits of RAG?"
    top_k = 5
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://127.0.0.1:8000/query" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

---

## Troubleshooting Windows-Specific Issues

### PowerShell Execution Policy

**Error:** "cannot be loaded because running scripts is disabled"

**Solution:**
```powershell
# As Administrator:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Ollama Not Starting

**Check if Ollama is running:**
```powershell
# Check process
Get-Process | Where-Object {$_.ProcessName -like "*ollama*"}

# If not running, start Ollama app from Start Menu
# Or run:
Start-Process "ollama"
```

### Port Already in Use

**Error:** "Address already in use: 8000"

**Solution:**
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill it (replace PID with actual process ID)
taskkill /PID [PID] /F

# Or use different port
python -m uvicorn rag.api.rag:app --reload --port 8080
```

### ChromaDB Issues on Windows

If you get SQLite errors:

```powershell
# Remove and rebuild indices
Remove-Item -Recurse -Force .chroma
Remove-Item -Recurse -Force .bm25

# Rebuild
python scripts/index_documents.py --rebuild
```

### Memory Issues

If Ollama crashes or system slows down:

1. **Use smaller model:**
   ```powershell
   ollama pull mistral:7b
   # Update .env: OLLAMA_MODEL=mistral:7b
   ```

2. **Reduce batch size:**
   ```powershell
   # Index fewer documents at a time
   python scripts/index_documents.py --limit 100
   ```

3. **Close other applications** while running

---

## Resource Optimization for Your Machine

### Check Your System

```powershell
# Check RAM
Get-CimInstance -ClassName Win32_ComputerSystem | Select-Object TotalPhysicalMemory

# Check CPU
Get-CimInstance -ClassName Win32_Processor | Select-Object Name, NumberOfCores
```

### Optimize Configuration Based on RAM

**8GB RAM:**
```bash
# .env settings
OLLAMA_MODEL=mistral:7b
TOP_K=3
VECTOR_TOP_K=6
BM25_TOP_K=12
CHUNK_SIZE=500
MAX_CONTEXT_TOKENS=3000
```

**16GB RAM:**
```bash
# .env settings
OLLAMA_MODEL=llama3:8b
TOP_K=5
VECTOR_TOP_K=10
BM25_TOP_K=20
CHUNK_SIZE=800
MAX_CONTEXT_TOKENS=6000
```

**32GB+ RAM:**
```bash
# .env settings
OLLAMA_MODEL=llama3:8b
TOP_K=8
VECTOR_TOP_K=16
BM25_TOP_K=30
CHUNK_SIZE=1000
MAX_CONTEXT_TOKENS=8000
```

---

## Quick Commands Cheatsheet

```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Deactivate
deactivate

# Check Ollama
ollama list

# Pull model
ollama pull llama3:8b

# Index documents
python scripts/index_documents.py --rebuild

# Run demo
python scripts/demo_wrong_right.py

# Start API
python -m uvicorn rag.api.rag:app --reload

# Run tests
pytest -v

# Verify setup
python scripts/verify_setup.py
```

---

## Next Steps

1. ✅ Verify Python installed: `python --version`
2. ✅ Verify Ollama installed: `ollama --version`
3. ✅ Pull model: `ollama pull llama3:8b`
4. ✅ Create venv: `python -m venv .venv`
5. ✅ Activate venv: `.\.venv\Scripts\Activate.ps1`
6. ✅ Install deps: `pip install -r requirements.txt`
7. ✅ Index docs: `python scripts/index_documents.py --rebuild`
8. ✅ Run demo: `python scripts/demo_medical_usecase.py`
9. ✅ Start API: `python -m uvicorn rag.api.rag:app --reload`

---

**Need help?** Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) or run:
```powershell
python scripts/verify_setup.py
```


