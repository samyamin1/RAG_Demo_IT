# RAG Demo - Main Files for Teaching

**For students/presentations: The essential files that tell the RAG story**

---

## 🎯 The RAG Story in 8 Files

Here's the journey of a question through the RAG system:

```
1. User asks question
   ↓
2. Document gets uploaded & processed (INGESTION)
   ↓
3. Text is chunked & embedded (CHUNKING)
   ↓
4. Question triggers search (RETRIEVAL)
   ↓
5. Best chunks are found & ranked (HYBRID SEARCH)
   ↓
6. Context is assembled (PROMPT BUILDING)
   ↓
7. LLM generates answer (GENERATION)
   ↓
8. Answer with citations returned
```

---

## 📁 Essential Files (Demo Flow)

### 1️⃣ **Entry Point** - `rag/core/service.py`

**What it does:** Orchestrates the entire RAG pipeline

**Key methods:**
```python
upload_document()      # Add new document
query_with_answer()    # Ask question, get cited answer
delete_document()      # Remove document
```

**The Story:**
> "This is the conductor. When you ask a question, this file coordinates 
> all the other components to give you an answer."

**Show students:**
- Line 44: `upload_document()` - starts the ingestion pipeline
- Line 76: `query_with_answer()` - starts the query pipeline

---

### 2️⃣ **Document Processing** - `rag/ingestion/ingest.py`

**What it does:** Breaks documents into chunks and creates embeddings

**Key methods:**
```python
parse_file()      # Read document
split_text()      # Break into chunks
embed_chunks()    # Create vector embeddings
```

**The Story:**
> "When you upload a document, this file chops it into bite-sized pieces 
> and turns each piece into a math vector (768 numbers)."

**Show students:**
- Line 52: Text splitting with overlap
- Line 77: Embedding creation (text → numbers)

---

### 3️⃣ **Vector Search** - `rag/retrieval/chroma.py`

**What it does:** Finds semantically similar chunks using vector math

**Key method:**
```python
similarity_search(query, k)  # Find k most similar chunks
```

**The Story:**
> "This is like Google search but for meanings. It finds chunks that MEAN 
> the same thing as your question, even if they use different words."

**Show students:**
- Line 85: Cosine similarity search
- Line 99: Converts distance to similarity score

---

### 4️⃣ **Keyword Search** - `rag/retrieval/bm25.py`

**What it does:** Finds chunks with matching keywords (like Ctrl+F but smarter)

**Key method:**
```python
search(query, k)  # Find k best keyword matches
```

**The Story:**
> "This is like Ctrl+F but smarter. It knows 'important' matches better 
> than repeated words. Finds chunks with your exact keywords."

**Show students:**
- Line 53: BM25 scoring algorithm
- Line 70: Gets top-k keyword matches

---

### 5️⃣ **Fusion** - `rag/retrieval/rrf.py`

**What it does:** Combines vector + keyword results into one ranked list

**Key function:**
```python
reciprocal_rank_fusion(vector_results, bm25_results)
```

**The Story:**
> "Two judges (vector & keyword) each rank the chunks. This combines both 
> rankings into one fair final ranking using math."

**Show students:**
- Line 28: RRF formula: `1/(60 + rank)`
- Line 33: Merges two ranked lists

**Math Example:**
```
Chunk appears at:
- Vector rank 2: score = 1/(60+2) = 0.016
- BM25 rank 5: score = 1/(60+5) = 0.015
- Combined: 0.031 (higher = better!)
```

---

### 6️⃣ **Context Builder** - `rag/assembler/context.py`

**What it does:** Formats retrieved chunks into a prompt for the LLM

**Key method:**
```python
build_prompt_context(retrieved_docs, query)
```

**The Story:**
> "Takes the top chunks and formats them nicely with [filename] tags so 
> the LLM knows where each piece came from."

**Show students:**
- Line 47: De-duplicates chunks
- Line 58: Adds [filename] headers
- Output format:
  ```
  [doc1.csv]
  Content here...
  
  [doc2.csv]
  More content...
  ```

---

### 7️⃣ **LLM Wrapper** - `rag/llm/ollama_wrapper.py`

**What it does:** Talks to Ollama to generate the final answer

**Key method:**
```python
generate_response(prompt, system_prompt)
```

**The Story:**
> "Sends the question + retrieved context to the AI model (llama3). 
> The model reads the context and writes an answer citing sources."

**Show students:**
- Line 47: Builds message with system prompt + context
- Line 63: Calls Ollama API
- Line 67: Returns generated text

---

### 8️⃣ **System Prompts** - `rag/prompts/system.py`

**What it does:** Instructions that tell the LLM how to behave

**Key prompt:**
```python
RAG_SYSTEM_PROMPT  # Instructions for cited answers
```

**The Story:**
> "These are the 'rules' we give the AI:
> 1. Always cite sources with [filename]
> 2. Never make up citations
> 3. Say 'I don't know' if context doesn't have the answer"

**Show students:**
- Line 5: RAG system prompt (read the instructions!)
- Line 30: Baseline prompt (no context version)

---

## 🎬 Demo Flow for Students

### **Live Demo Script:**

**Step 1: Show the Question**
```python
question = "How do I reset my PIN?"
```

**Step 2: Show WITHOUT RAG** (`scripts/demo_final.py` line 30)
```python
# Generic LLM answer (may be wrong!)
llm.generate_response(question, GENERIC_PROMPT)
→ Talks about banking (WRONG!)
```

**Step 3: Show WITH RAG** (`scripts/demo_final.py` line 48)
```python
# RAG pipeline
rag_service.query_with_answer(question)
→ Company IT portal procedure (RIGHT!)
```

**Step 4: Trace Through Files**

```
User Question: "How do I reset my PIN?"
    ↓
[service.py] CentralizedRAGService.query_with_answer()
    ↓
[hybrid.py] DocumentRetrievalService.query_documents()
    ↓ (splits into two paths)
    ├─> [chroma.py] Vector search → finds semantically similar chunks
    └─> [bm25.py] Keyword search → finds chunks with "PIN", "reset"
    ↓
[rrf.py] Combines rankings → top 5 chunks
    ↓
[context.py] Formats chunks with [filename] tags
    ↓
[ollama_wrapper.py] Sends to LLM with context
    ↓
Answer: "According to [kaggle_dataset], go to intranet..."
```

---

## 📝 Quick File Summary Table

| File | Line Count | Purpose | Show This |
|------|------------|---------|-----------|
| **service.py** | 120 | Main orchestrator | Entry point for everything |
| **ingest.py** | 120 | Document processing | How text becomes chunks |
| **chroma.py** | 140 | Vector search | Semantic similarity magic |
| **bm25.py** | 130 | Keyword search | Traditional search |
| **rrf.py** | 80 | Fusion algorithm | How two rankings become one |
| **context.py** | 100 | Prompt builder | How context is formatted |
| **ollama_wrapper.py** | 166 | LLM integration | How we talk to AI |
| **system.py** | 75 | Prompts | The "rules" for AI |

**Total:** ~900 lines tell the complete RAG story!

---

## 🎓 Teaching Points

### Point 1: Why Hybrid Search?

**Show:** `rag/retrieval/hybrid.py` line 47

```python
# Two search methods working together
vector_results = vector_store.similarity_search(query)  # Meaning
bm25_results = bm25_store.search(query)                # Keywords
fused = rrf_fusion(vector_results, bm25_results)       # Best of both
```

**Explain:**
- Vector finds "similar meaning" (PIN reset → password recovery)
- BM25 finds "exact words" (PIN, reset)
- Together: Better than either alone!

---

### Point 2: Why Citations Matter

**Show:** `rag/prompts/system.py` line 11

```python
"Always reference specific documents when making claims. 
Use the format [filename]"
```

**Explain:**
- Without this: LLM might make things up
- With this: Every claim must cite a source
- Result: Verifiable, trustworthy answers

---

### Point 3: The Magic of Embeddings

**Show:** `rag/ingestion/ingest.py` line 84

```python
embeddings = self.embeddings.embed_documents(texts)
# Turns text into 768-dimensional vectors
```

**Explain:**
- Text: "Reset your PIN" 
- Becomes: [0.23, -0.45, 0.67, ...] (768 numbers)
- Similar text = similar vectors
- Math can find similar vectors = find similar text!

---

## 🎮 Interactive Demo for Students

### Demo Script (5 minutes):

**1. Show the Dataset (30 sec)**
```powershell
# Show what we have
python -c "import pandas as pd; print(pd.read_csv('data/raw/rag_sample_qas_from_kis.csv')[['ki_topic']].head())"
```
> "10 IT support documents about email, PIN reset, printers..."

**2. Show Indexing (30 sec)**
```powershell
# Already done, but explain
# "We broke 10 docs into 72 chunks and created vector embeddings"
```

**3. Run Demo (3 min)**
```powershell
python scripts/demo_final.py
```
> Watch both answers appear live!

**4. Explain Difference (1 min)**
- Without RAG: "Contact your bank" ❌ WRONG
- With RAG: "Go to company intranet portal" ✅ RIGHT
> "RAG prevented hallucination by using actual company docs!"

---

## 📂 File Organization for Presentation

### **Slide 1: The Problem**
> "LLMs are smart but don't know YOUR company's specific procedures"

### **Slide 2: The Solution - RAG Architecture**
Show diagram:
```
Question → Retrieval → Context → LLM → Cited Answer
```

### **Slide 3: Key File - service.py**
> "The orchestrator that runs the whole show"

### **Slide 4: Ingestion - ingest.py**
> "How documents become searchable chunks"

### **Slide 5: Hybrid Search - chroma.py + bm25.py + rrf.py**
> "Finding the right context using vector + keyword search"

### **Slide 6: Context Builder - context.py**
> "Formatting retrieved chunks for the LLM"

### **Slide 7: LLM - ollama_wrapper.py**
> "Generating the final answer with citations"

### **Slide 8: Live Demo**
> Run `python scripts/demo_final.py`

### **Slide 9: Results**
> Show side-by-side comparison from DEMO_RESULTS_DOCUMENTED.md

---

## 💡 Simple Analogies for Students

### RAG is like writing a research paper:

**Without RAG (Generic LLM):**
- Student writes from memory
- No sources
- Might be wrong
- Can't verify

**With RAG:**
- Student researches first (RETRIEVAL)
- Finds relevant books (VECTOR + BM25)
- Takes notes (CHUNKING)
- Writes paper citing sources (GENERATION)
- Every claim has a footnote (CITATIONS)

### Components = Team Members:

- **service.py** = Project Manager (coordinates everyone)
- **ingest.py** = Librarian (organizes books)
- **chroma.py** = Smart Search (finds by meaning)
- **bm25.py** = Index Search (finds by keywords)
- **rrf.py** = Ranker (picks best results)
- **context.py** = Note-taker (summarizes findings)
- **ollama_wrapper.py** = Writer (writes the answer)
- **system.py** = Editor (sets the rules)

---

## 🎯 The 3-Minute Explanation

**1. The Problem (30 sec):**
> "LLMs know general facts but not YOUR specific company procedures. 
> They might hallucinate or give wrong advice."

**2. The Solution (30 sec):**
> "RAG = Retrieval Augmented Generation. Before answering, RETRIEVE 
> relevant documents from YOUR knowledge base, then generate answer 
> using that context."

**3. How It Works (90 sec):**

```
Upload → ingest.py → Chunks + Embeddings
                          ↓
                    Stored in ChromaDB + BM25
                          ↓
Query → hybrid.py → Search both indexes
                          ↓
                    rrf.py → Combine results
                          ↓
                    context.py → Format context
                          ↓
                    ollama_wrapper.py → Generate answer
                          ↓
                    Answer with [source citations]
```

**4. The Proof (30 sec):**
> "Watch: Same question, two answers.
> Without RAG: Generic, sometimes wrong
> With RAG: Specific, cited, correct"

---

## 📚 Files to Open During Demo

### Core Files (Open these side-by-side):

**1. service.py** (lines 76-110)
```python
def query_with_answer(self, query, top_k):
    # Retrieve documents
    retrieved_docs = self.retrieval_service.query_documents(query)
    
    # Build context
    context = self.context_assembler.build_prompt_context(retrieved_docs)
    
    # Generate answer
    answer = self.llm.generate_response(prompt)
    
    return QueryResponse(answer, sources)
```
> "This is the complete RAG pipeline in 15 lines!"

**2. hybrid.py** (lines 47-75)
```python
def query_documents(self, query, top_k):
    # Vector search
    vector_results = self.vector_store.similarity_search(query)
    
    # Keyword search
    bm25_results = self.bm25_store.search(query)
    
    # Combine
    fused_results = reciprocal_rank_fusion(vector_results, bm25_results)
    
    return fused_results
```
> "Hybrid search: Vector finds meaning, BM25 finds keywords, RRF combines!"

**3. rrf.py** (lines 8-50)
```python
def reciprocal_rank_fusion(vector_results, bm25_results, k=60):
    for rank, doc in enumerate(vector_results):
        score = 1 / (k + rank)  # The magic formula!
```
> "Simple formula that makes two ranked lists become one!"

---

## 🎪 Demo Script for Presentation

```python
# === LIVE DEMO CODE ===

from rag.core.service import CentralizedRAGService
from rag.llm.ollama_wrapper import LocalLLMWrapper
from rag.prompts.system import GENERIC_NO_CONTEXT_SYSTEM_PROMPT

# Initialize
rag = CentralizedRAGService()
llm = LocalLLMWrapper()

question = "How do I reset my PIN?"

# WITHOUT RAG
print("=== WITHOUT RAG ===")
answer1 = llm.generate_response(
    prompt=f"Question: {question}",
    system_prompt=GENERIC_NO_CONTEXT_SYSTEM_PROMPT
)
print(answer1)
print("\nSources: None")

# WITH RAG  
print("\n=== WITH RAG ===")
response = rag.query_with_answer(question)
print(response.answer)
print(f"\nSources: {len(response.sources)} documents")
for src in response.sources:
    print(f"  - {src.filename} (score: {src.score:.3f})")
```

**Expected output:**
- Answer 1: Generic banking advice ❌
- Answer 2: Company IT portal steps ✅ with citations

---

## 🔑 Key Files Cheat Sheet

| File | Purpose | Key Concept |
|------|---------|-------------|
| `service.py` | Orchestrator | "The conductor" |
| `ingest.py` | Processing | "Text → Chunks → Vectors" |
| `chroma.py` | Vector search | "Find by meaning" |
| `bm25.py` | Keyword search | "Find by words" |
| `rrf.py` | Fusion | "Combine rankings" |
| `context.py` | Prompt builder | "Format context" |
| `ollama_wrapper.py` | LLM | "Generate answer" |
| `system.py` | Instructions | "Citation rules" |

---

## 📊 Visual Flow Diagram

```
USER QUESTION: "How do I reset my PIN?"
       │
       ▼
┌──────────────────────┐
│   service.py         │  ← Receives question
│   query_with_answer()│
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   hybrid.py          │  ← Searches both indexes
│   query_documents()  │
└──────┬───────────────┘
       │
       ├─────────────────┐
       ▼                 ▼
┌─────────────┐   ┌──────────────┐
│  chroma.py  │   │   bm25.py    │
│   Vector    │   │   Keyword    │
│   Search    │   │   Search     │
└──────┬──────┘   └──────┬───────┘
       │                 │
       └────────┬────────┘
                ▼
       ┌─────────────────┐
       │    rrf.py       │  ← Combines results
       │ Rank Fusion     │
       └────────┬────────┘
                ▼
         Top 5 chunks
                │
                ▼
       ┌─────────────────┐
       │  context.py     │  ← Formats with [filename]
       │ build_context() │
       └────────┬────────┘
                ▼
         Formatted context
                │
                ▼
       ┌──────────────────┐
       │ ollama_wrapper.py│  ← Generates answer
       │ + system.py      │
       └────────┬─────────┘
                ▼
    "According to [doc.csv]..."
    WITH CITATIONS!
```

---

## 🎯 For Your Presentation

### **What to Show:**

**1. The Problem (1 min):**
- Generic LLM gives wrong answer (banking vs IT)
- No sources = can't verify
- May violate company policy

**2. The Solution (1 min):**
- RAG retrieves company docs FIRST
- LLM answers using THOSE docs
- Cites sources = verifiable

**3. The Files (3 min):**
Walk through the 8 files showing:
- Where documents go in (ingest.py)
- How search works (chroma.py, bm25.py)
- How fusion works (rrf.py)
- How LLM uses context (ollama_wrapper.py)

**4. Live Demo (2 min):**
- Run: `python scripts/demo_final.py`
- Show both answers
- Highlight the difference

**5. Q&A (3 min)**

**Total: 10 minutes**

---

## 📦 Files to Have Open

**For IDE demo, open these in tabs:**

1. `rag/core/service.py` - Start here
2. `rag/retrieval/hybrid.py` - Show hybrid search
3. `rag/retrieval/rrf.py` - Show fusion formula
4. `rag/llm/ollama_wrapper.py` - Show LLM call
5. `scripts/demo_final.py` - Run this live

**5 files = Complete RAG story!**

---

## 🚀 One-Slide Summary

```
╔════════════════════════════════════════════════════════════╗
║                    RAG IN 8 FILES                          ║
╚════════════════════════════════════════════════════════════╝

1. service.py       → Orchestrates everything
2. ingest.py        → Document → Chunks → Embeddings
3. chroma.py        → Vector search (meaning)
4. bm25.py          → Keyword search (words)
5. rrf.py           → Fusion (combine rankings)
6. context.py       → Format context with [sources]
7. ollama_wrapper.py→ LLM generates answer
8. system.py        → Citation rules

RESULT: Generic LLM → Cited, Specific, Accurate RAG!
```

---

## 💡 Simplest Possible Explanation

**RAG in one sentence:**
> "Instead of asking the AI to remember everything, we let it Google 
> through YOUR documents first, then answer using what it found."

**Files in one sentence each:**
- `service.py` - The boss that tells everyone what to do
- `ingest.py` - Chops documents into searchable pieces  
- `chroma.py` - Finds chunks that MEAN the same thing
- `bm25.py` - Finds chunks with the same WORDS
- `rrf.py` - Picks the best chunks from both searches
- `context.py` - Organizes chunks into a neat package
- `ollama_wrapper.py` - Asks the AI to write an answer
- `system.py` - Rules: "Always cite your sources!"

---

## ✅ Summary

**For students, focus on:**
1. ✅ 8 core files (not all 72!)
2. ✅ The flow: Upload → Index → Query → Retrieve → Generate
3. ✅ Why hybrid search (vector + keyword)
4. ✅ Why citations matter
5. ✅ Live demo showing clear difference

**Keep it simple, show working code, let results speak!**

**Run:** `python scripts/demo_final.py` and watch their faces! 😊

