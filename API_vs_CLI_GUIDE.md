# API vs CLI Commands - Complete Guide

## Overview

You have **TWO ways** to use the RAG system:

1. **FastAPI REST API** - Web service for integration
2. **Python CLI Commands** - Direct Python scripts

---

## Option 1: FastAPI REST API

### What It Does:
- Provides **HTTP endpoints** (like a web service)
- Allows **any application** to use RAG (not just Python)
- Can be accessed from:
  - Web browsers
  - Mobile apps
  - Other programming languages (JavaScript, Java, etc.)
  - curl/Postman
  - Remote machines

### When to Use:
- ✅ Building a web application
- ✅ Need to integrate with non-Python code
- ✅ Want multiple users/apps to access RAG
- ✅ Need remote access
- ✅ Want to test in browser (Swagger UI)

### How It Works:

**Step 1: Start the server**
```powershell
python -m uvicorn rag.api.rag:app --reload --host 127.0.0.1 --port 8000
```

**Step 2: Access endpoints**

Available endpoints:
- `GET /health` - Check system status
- `POST /upload` - Add documents to knowledge base
- `POST /query` - Ask questions with RAG
- `DELETE /delete?doc_id=XXX` - Remove documents
- `GET /status` - Get detailed status

**Step 3: Use from anywhere**

From browser:
```
http://127.0.0.1:8000/docs  (Interactive Swagger UI)
```

From PowerShell:
```powershell
$body = @{query = "How do I reset my PIN?"; top_k = 5} | ConvertTo-Json
Invoke-WebRequest -Uri http://127.0.0.1:8000/query -Method POST -ContentType "application/json" -Body $body
```

From Python:
```python
import requests
response = requests.post(
    "http://127.0.0.1:8000/query",
    json={"query": "How do I reset my PIN?", "top_k": 5}
)
print(response.json())
```

From JavaScript:
```javascript
fetch('http://127.0.0.1:8000/query', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({query: "How do I reset my PIN?", top_k: 5})
})
```

---

## Option 2: Python CLI Commands

### What It Does:
- Runs RAG **directly in Python**
- No web server needed
- Import and use the library directly

### When to Use:
- ✅ Quick testing
- ✅ Python-only projects
- ✅ Batch processing
- ✅ Local scripts
- ✅ Development/debugging

### How It Works:

**Direct Python import:**
```python
from rag.core.service import CentralizedRAGService

# Initialize
rag = CentralizedRAGService()

# Query
response = rag.query_with_answer("How do I reset my PIN?")
print(response.answer)

# View sources
for src in response.sources:
    print(f"{src.filename}: {src.score:.3f}")
```

**One-line command:**
```powershell
python -c "from rag.core.service import CentralizedRAGService; rag = CentralizedRAGService(); print(rag.query_with_answer('How do I reset my PIN?').answer)"
```

**Script files:**
```powershell
# Run demo
python scripts/demo_final.py

# Run tests
pytest -v

# Verify setup
python scripts/verify_setup.py
```

---

## Comparison Table

| Feature | FastAPI (Web API) | Python CLI |
|---------|-------------------|------------|
| **Setup** | Start server first | Import directly |
| **Access** | HTTP (any language) | Python only |
| **Use Case** | Web apps, integrations | Scripts, testing |
| **Multiple Users** | ✅ Yes (concurrent) | ❌ No (one at a time) |
| **Remote Access** | ✅ Yes (over network) | ❌ No (local only) |
| **Browser UI** | ✅ Yes (Swagger) | ❌ No |
| **Speed** | Slower (HTTP overhead) | Faster (direct) |
| **Best For** | Production apps | Development, testing |

---

## Examples

### Scenario 1: You're building a chatbot web app

**Use FastAPI:**
```
1. Start API: python -m uvicorn rag.api.rag:app
2. Your web app sends HTTP requests to http://127.0.0.1:8000/query
3. Display results in your chatbot UI
```

### Scenario 2: You want to test a quick question

**Use Python CLI:**
```python
from rag.core.service import CentralizedRAGService
rag = CentralizedRAGService()
print(rag.query_with_answer("What is the PIN reset procedure?").answer)
```

### Scenario 3: You want to batch process 100 questions

**Use Python CLI:**
```python
from rag.core.service import CentralizedRAGService
rag = CentralizedRAGService()

questions = [...]  # Your 100 questions
for q in questions:
    response = rag.query_with_answer(q)
    save_to_file(response)
```

### Scenario 4: You want to integrate with a JavaScript frontend

**Use FastAPI:**
```javascript
// Frontend JavaScript
async function askRAG(question) {
  const response = await fetch('http://127.0.0.1:8000/query', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({query: question, top_k: 5})
  });
  return await response.json();
}
```

---

## Which Should You Use?

### Use **FastAPI** if:
- Building a web application
- Need API for frontend
- Want remote access
- Multiple users/apps will use it
- Need cross-platform access

### Use **Python CLI** if:
- Quick testing
- Python-only project
- Batch processing
- Development
- No web server needed

### Use **BOTH** if:
- Developing: Use CLI for quick tests
- Production: Deploy with API for users

---

## Summary

**API = Web Service (any app can use it)**
**CLI = Direct Python (Python scripts only)**

Both do the same RAG functionality, just different access methods!

