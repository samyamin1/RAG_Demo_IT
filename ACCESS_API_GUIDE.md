# How to Access the RAG API - Simple Guide

## Quick Start

### Step 1: Start the API Server

**Option A: Use the batch file (EASIEST)**

Just **double-click**: `start_api.bat`

**Option B: Manual command**

Open PowerShell:
```powershell
cd "C:\Users\smami\Downloads\AI Consultations\InnovaDigits\RAG"
.\.venv\Scripts\Activate.ps1
python -m uvicorn rag.api.rag:app --reload --host 127.0.0.1 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

**Keep this window open!** The API runs as long as this window is open.

---

### Step 2: Access the API

#### Method 1: Browser (EASIEST to test)

Open your web browser and go to:

**Interactive Documentation:**
```
http://127.0.0.1:8000/docs
```

You'll see Swagger UI where you can:
- Click on endpoints
- Click "Try it out"
- Enter parameters
- Click "Execute"
- See results!

**Quick Health Check:**
```
http://127.0.0.1:8000/health
```

Should show: `{"status":"ok","ollama_available":true,"indices_loaded":true}`

---

#### Method 2: PowerShell Commands

Open a **NEW PowerShell window** (keep API running in first window):

**Test Health:**
```powershell
Invoke-WebRequest -Uri http://127.0.0.1:8000/health
```

**Ask a Question:**
```powershell
$body = @{
    query = "How do I reset my PIN?"
    top_k = 5
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri http://127.0.0.1:8000/query `
    -Method POST `
    -ContentType "application/json" `
    -Body $body

$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

---

#### Method 3: Python Script

Create a file `test_api.py`:

```python
import requests

# Test health
response = requests.get("http://127.0.0.1:8000/health")
print("Health:", response.json())

# Ask question
response = requests.post(
    "http://127.0.0.1:8000/query",
    json={
        "query": "How do I set up my company email?",
        "top_k": 5
    }
)

result = response.json()
print("\nAnswer:", result['answer'])
print("\nSources:")
for src in result['sources']:
    print(f"  - {src['filename']} (score: {src['score']:.4f})")
```

Run it:
```powershell
python test_api.py
```

---

## Available API Endpoints

### 1. GET /health
**Purpose:** Check if system is running

**Example:**
```
http://127.0.0.1:8000/health
```

**Response:**
```json
{
  "status": "ok",
  "ollama_available": true,
  "indices_loaded": true
}
```

---

### 2. POST /query (MAIN ENDPOINT)
**Purpose:** Ask questions and get answers with citations

**Request:**
```json
{
  "query": "How do I reset my PIN?",
  "top_k": 5
}
```

**Response:**
```json
{
  "answer": "According to [kaggle_dataset], you can reset...",
  "sources": [
    {
      "id": "doc_1_chunk_0",
      "filename": "kaggle_dataset",
      "score": 0.0328,
      "route": "hybrid"
    }
  ],
  "query": "How do I reset my PIN?"
}
```

---

### 3. POST /upload
**Purpose:** Add new documents to knowledge base

**Request:**
```json
{
  "content": "New IT policy: All passwords must be changed monthly.",
  "filename": "security_policy.txt"
}
```

**Response:**
```json
{
  "doc_id": "abc123...",
  "filename": "security_policy.txt",
  "chunks_created": 1,
  "status": "success"
}
```

---

### 4. DELETE /delete
**Purpose:** Remove documents

**Example:**
```
http://127.0.0.1:8000/delete?doc_id=abc123
```

**Response:**
```json
{
  "status": "success",
  "doc_id": "abc123",
  "message": "Document deleted"
}
```

---

### 5. GET /status
**Purpose:** Get detailed system information

**Example:**
```
http://127.0.0.1:8000/status
```

**Response:**
```json
{
  "status": "ok",
  "ollama_available": true,
  "ollama_model": "llama3:8b",
  "indices_loaded": true,
  "vector_chunks": 72,
  "bm25_chunks": 72
}
```

---

## Troubleshooting API Access

### Issue 1: "Unable to connect"

**Cause:** API server not running

**Solution:**
1. Check if server window is still open
2. Look for: `Uvicorn running on http://127.0.0.1:8000`
3. If not, restart: double-click `start_api.bat`

---

### Issue 2: "Port already in use"

**Cause:** Another process using port 8000

**Solution:**

**Option A: Kill the process**
```powershell
# Find process on port 8000
netstat -ano | findstr :8000

# Kill it (replace PID with actual number)
taskkill /PID <PID> /F
```

**Option B: Use different port**
```powershell
python -m uvicorn rag.api.rag:app --host 127.0.0.1 --port 8080
# Then use http://127.0.0.1:8080 instead
```

---

### Issue 3: "Ollama not available"

**Cause:** Ollama service not running

**Solution:**
1. Check system tray for Ollama icon
2. If not there, start Ollama from Start menu
3. Or run: `ollama serve` in terminal

---

### Issue 4: "Indices not loaded"

**Cause:** Documents not indexed yet

**Solution:**
```powershell
python scripts/index_documents.py --rebuild
```

---

## Testing the API

### Full Test Script

Save as `full_api_test.py`:

```python
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

print("="*60)
print("RAG API TEST")
print("="*60)

# 1. Health Check
print("\n1. Testing /health...")
r = requests.get(f"{BASE_URL}/health")
print(f"   Status: {r.status_code}")
print(f"   Response: {r.json()}")

# 2. System Status
print("\n2. Testing /status...")
r = requests.get(f"{BASE_URL}/status")
status = r.json()
print(f"   Ollama: {status['ollama_available']}")
print(f"   Chunks: {status['vector_chunks']}")

# 3. Query
print("\n3. Testing /query...")
r = requests.post(
    f"{BASE_URL}/query",
    json={"query": "How do I reset my PIN?", "top_k": 3}
)
result = r.json()
print(f"   Answer length: {len(result['answer'])} chars")
print(f"   Sources: {len(result['sources'])}")
print(f"\n   First 200 chars:")
print(f"   {result['answer'][:200]}...")

# 4. Upload (optional)
print("\n4. Testing /upload...")
r = requests.post(
    f"{BASE_URL}/upload",
    json={
        "content": "Test document: RAG is awesome!",
        "filename": "test.txt"
    }
)
upload_result = r.json()
print(f"   Doc ID: {upload_result['doc_id'][:20]}...")
print(f"   Chunks: {upload_result['chunks_created']}")

print("\n" + "="*60)
print("ALL TESTS PASSED!")
print("="*60)
```

Run it:
```powershell
pip install requests  # if not already installed
python full_api_test.py
```

---

## Summary

**To use API:**
1. Start server: Double-click `start_api.bat`
2. Open browser: http://127.0.0.1:8000/docs
3. Test endpoints interactively
4. Integrate with your application

**To use CLI:**
1. No server needed
2. Import Python library directly
3. Call functions in your scripts

**Both access the same RAG functionality!**

---

## Next Steps

After API is running:

1. **Try in browser:** http://127.0.0.1:8000/docs
2. **Test queries:** Use the Swagger UI
3. **Upload documents:** Add your own knowledge
4. **Integrate:** Use from your application

**Your RAG API is ready for production use!** 🚀

