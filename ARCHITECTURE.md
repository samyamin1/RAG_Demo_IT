# RAG Module Architecture

Detailed architecture documentation mapping code modules to the system design.

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI REST API Layer                      │
│              (rag/api/rag.py - /upload, /query, /delete)        │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                  CentralizedRAGService                           │
│                   (rag/core/service.py)                          │
│                  Orchestrates entire pipeline                    │
└─┬───────────────────┬──────────────────┬───────────────────┬────┘
  │                   │                  │                   │
  ▼                   ▼                  ▼                   ▼
┌─────────────┐ ┌────────────┐ ┌───────────────┐ ┌──────────────┐
│  Ingestion  │ │ Retrieval  │ │   Context     │ │  LLM Wrapper │
│   Service   │ │  Service   │ │  Assembler    │ │  (Ollama)    │
└─────────────┘ └────────────┘ └───────────────┘ └──────────────┘
```

---

## Component Breakdown

### 1. API Layer

**File:** `rag/api/rag.py`

**Purpose:** FastAPI REST endpoints for external access

**Endpoints:**

| Endpoint | Method | Purpose | Request | Response |
|----------|--------|---------|---------|----------|
| `/` | GET | Root info | - | JSON with links |
| `/health` | GET | Health check | - | `HealthResponse` |
| `/status` | GET | Detailed status | - | Status dict |
| `/upload` | POST | Upload document | `UploadRequest` | `UploadResponse` |
| `/query` | POST | Query with RAG | `QueryRequest` | `QueryResponse` |
| `/delete` | DELETE | Delete document | `?doc_id=...` | Success message |
| `/reset` | POST | Reset all indices | - | Success message |

**Key Features:**
- ✅ OpenAPI/Swagger docs at `/docs`
- ✅ Input validation via Pydantic
- ✅ Error handling with HTTP status codes
- ✅ CORS support (configurable)

---

### 2. CentralizedRAGService (Orchestration Layer)

**File:** `rag/core/service.py`

**Class:** `CentralizedRAGService`

**Purpose:** Main orchestration hub that coordinates all components

**Methods:**

```python
class CentralizedRAGService:
    def upload_document(content, filename, doc_id, metadata) -> Dict:
        """Pipeline: parse → chunk → embed → index"""
    
    def query_with_answer(query, top_k, temperature) -> QueryResponse:
        """Pipeline: retrieve → assemble → generate → cite"""
    
    def delete_document(doc_id):
        """Remove from both vector and BM25 stores"""
    
    def get_status() -> Dict:
        """System health and counts"""
    
    def reset_indices():
        """Wipe all data (for rebuilding)"""
```

**Sequence Diagram - Query Flow:**

```
User → query_with_answer(query)
  │
  ├─→ DocumentRetrievalService.query_documents(query)
  │   ├─→ ChromaVectorStore.similarity_search()
  │   ├─→ BM25Store.search()
  │   └─→ RRF.reciprocal_rank_fusion()
  │   └─→ returns: List[RetrievedDoc]
  │
  ├─→ ContextAssembler.build_prompt_context(retrieved_docs)
  │   └─→ returns: formatted_context (with [filename] headers)
  │
  ├─→ ContextAssembler.build_full_prompt(query, context)
  │   └─→ returns: complete_prompt
  │
  ├─→ LocalLLMWrapper.generate_response(prompt, RAG_SYSTEM_PROMPT)
  │   └─→ returns: answer_text
  │
  └─→ Build QueryResponse(answer, sources, query)
      └─→ returns to User
```

---

### 3. Document Ingestion Service

**File:** `rag/ingestion/ingest.py`

**Class:** `DocumentIngestionService`

**Purpose:** Parse, chunk, and embed documents

**Methods:**

```python
class DocumentIngestionService:
    def parse_file(content, filename, doc_id, metadata) -> Document:
        """Convert raw content to Document object"""
    
    def split_text(document) -> List[Chunk]:
        """Split into overlapping chunks using RecursiveCharacterTextSplitter"""
    
    def embed_chunks(chunks) -> List[List[float]]:
        """Generate embeddings via OllamaEmbeddings"""
    
    def process_document(content, filename, ...) -> (Document, List[Chunk], embeddings):
        """Full pipeline: parse → split → embed"""
```

**Chunking Strategy:**
- Uses LangChain's `RecursiveCharacterTextSplitter`
- Separators: `["\n\n", "\n", ". ", " ", ""]`
- Chunk size: `CHUNK_SIZE` tokens (default 800)
- Overlap: `CHUNK_OVERLAP` tokens (default 120)
- Preserves sentence/paragraph boundaries where possible

**Embedding:**
- Model: `nomic-embed-text` (default, configurable)
- Dimension: 384 (for nomic-embed-text)
- Provider: Ollama local embeddings

---

### 4. Document Retrieval Service (Hybrid)

**File:** `rag/retrieval/hybrid.py`

**Class:** `DocumentRetrievalService`

**Purpose:** Combine vector + BM25 search with RRF fusion

#### 4.1 Vector Store (ChromaDB)

**File:** `rag/retrieval/chroma.py`

**Class:** `ChromaVectorStore`

**Methods:**
```python
class ChromaVectorStore:
    def add_chunks(chunks, embeddings):
        """Add to ChromaDB with metadata"""
    
    def similarity_search(query, k) -> List[RetrievedDoc]:
        """Cosine similarity search, returns top-k"""
    
    def delete_document(doc_id):
        """Remove all chunks of a document"""
```

**Key Details:**
- **Distance metric:** Cosine similarity
- **Storage:** Persistent (`.chroma/` directory)
- **Index:** HNSW (Hierarchical Navigable Small World)
- **Metadata:** doc_id, filename, chunk_index, title, tags

#### 4.2 BM25 Store (Lexical)

**File:** `rag/retrieval/bm25.py`

**Class:** `BM25Store`

**Methods:**
```python
class BM25Store:
    def add_chunks(chunks):
        """Build BM25Okapi index"""
    
    def search(query, k) -> List[RetrievedDoc]:
        """BM25 scoring, returns top-k"""
    
    def tokenize(text) -> List[str]:
        """Simple whitespace + lowercase tokenization"""
```

**Key Details:**
- **Algorithm:** BM25Okapi (from `rank_bm25`)
- **Parameters:** `k1` (term frequency saturation), `b` (length normalization)
- **Storage:** Pickled to `.bm25/` directory
- **Tokenization:** Simple split + lowercase (can be enhanced)

#### 4.3 RRF Fusion

**File:** `rag/retrieval/rrf.py`

**Function:** `reciprocal_rank_fusion(vector_results, bm25_results, k, top_k)`

**Algorithm:**

```
For each document d:
    RRF_score(d) = Σ [ 1 / (k + rank_i(d)) ]
    
Where:
    k = constant (default 60)
    rank_i(d) = rank of d in result list i
    Σ = sum over all result lists where d appears
```

**Example:**

```python
# Document appears at rank 2 in vector, rank 1 in BM25
# k = 60

RRF_score = 1/(60+2) + 1/(60+1)
          = 1/62 + 1/61
          = 0.0161 + 0.0164
          = 0.0325
```

**Why RRF?**
- ✅ No score normalization needed
- ✅ Handles different score scales naturally
- ✅ Promotes documents that rank well in multiple systems
- ✅ Well-studied, proven effective

---

### 5. Context Assembler (Prompt Builder)

**File:** `rag/assembler/context.py`

**Class:** `ContextAssembler`

**Methods:**

```python
class ContextAssembler:
    def build_prompt_context(retrieved_docs, query) -> str:
        """Format retrieved chunks with [filename] headers"""
    
    def build_full_prompt(query, context, system_prompt) -> str:
        """Combine system + context + query"""
    
    def estimate_tokens(text) -> int:
        """Rough token count (chars / 4)"""
```

**Output Format:**

```
[doc_023.csv]
Retrieval augmented generation combines retrieval with language models
to improve accuracy by grounding responses in specific knowledge bases.

[doc_045.csv]
RAG reduces hallucinations by requiring the model to cite sources and
only use information from the retrieved context.

[doc_089.csv]
...
```

**Token Budget Management:**
- Tracks cumulative token count
- Stops adding chunks when approaching `MAX_CONTEXT_TOKENS`
- De-duplicates by (doc_id, chunk_index)
- Prioritizes higher-ranked chunks

---

### 6. LocalLLMWrapper (Ollama Integration)

**File:** `rag/llm/ollama_wrapper.py`

**Classes:** `LocalLLMWrapper`, `OllamaEmbeddings`

#### 6.1 LocalLLMWrapper

```python
class LocalLLMWrapper:
    def generate_response(prompt, system_prompt, max_tokens, temperature, stop_seqs) -> str:
        """Generate text via Ollama chat API"""
    
    def check_available() -> bool:
        """Verify model is pulled"""
    
    def pull_model():
        """Download model if not present"""
```

**Chat Template Support:**
- Llama 3 format (default)
- Mistral format
- ChatML format
- Auto-detection based on model name

**Generation Parameters:**
- `temperature`: 0.2 (default, configurable)
- `max_tokens`: 1024 (default)
- `stop_sequences`: Configurable
- `context_window`: Model-dependent

#### 6.2 OllamaEmbeddings

```python
class OllamaEmbeddings:
    def embed_documents(texts) -> List[List[float]]:
        """Batch embed multiple texts"""
    
    def embed_query(text) -> List[float]:
        """Embed single query"""
```

**Default Model:** `nomic-embed-text` (768d)

**Alternative:** Can use Ollama's embedding endpoint for any model

---

### 7. Prompts and System Instructions

**File:** `rag/prompts/system.py`

**Key Prompts:**

#### RAG_SYSTEM_PROMPT

```
You are a helpful AI assistant with access to a knowledge base.

Instructions:
1. Cite sources by filename [filename] or [doc_id]
2. Be evidence-based - only use provided context
3. Admit uncertainty if context insufficient
4. Be concise but thorough
5. Never fabricate citations
```

#### GENERIC_NO_CONTEXT_SYSTEM_PROMPT

Used for "wrong" (no RAG) baseline in demos:
```
You are a helpful AI assistant. Answer based on your general knowledge.
```

---

### 8. Type System

**File:** `rag/types.py`

**Key Models (Pydantic):**

```python
class Document(BaseModel):
    """Source document"""
    id: str
    title: str
    content: str
    tags: List[str]
    source: str
    metadata: dict

class Chunk(BaseModel):
    """Text chunk from document"""
    id: str
    doc_id: str
    content: str
    chunk_index: int
    filename: str
    metadata: dict

class RetrievedDoc(BaseModel):
    """Retrieved chunk with score"""
    id: str
    doc_id: str
    filename: str
    content: str
    score: float
    route: Literal["vector", "bm25", "hybrid"]

class QueryResponse(BaseModel):
    """Final response with citations"""
    answer: str
    sources: List[SourceRef]
    query: str
```

---

### 9. Configuration

**File:** `rag/config.py`

**Class:** `Settings` (Pydantic BaseSettings)

Loads from:
1. `.env` file
2. Environment variables
3. Default values

**Key Settings:**
- Ollama model and URL
- Storage directories
- Retrieval parameters (TOP_K, RRF_K, etc.)
- Chunking parameters
- LLM generation parameters

**Function:** `print_config()` - Displays effective configuration at startup

---

## Data Flow

### Upload Flow

```
1. API receives UploadRequest
   ↓
2. CentralizedRAGService.upload_document()
   ↓
3. DocumentIngestionService:
   - parse_file() → Document
   - split_text() → List[Chunk]
   - embed_chunks() → List[embeddings]
   ↓
4. DocumentRetrievalService:
   - vector_store.add_chunks(chunks, embeddings)
   - bm25_store.add_chunks(chunks)
   ↓
5. Return UploadResponse(doc_id, chunks_created)
```

### Query Flow

```
1. API receives QueryRequest(query, top_k)
   ↓
2. CentralizedRAGService.query_with_answer()
   ↓
3. DocumentRetrievalService.query_documents():
   ├─ vector_store.similarity_search(query, vector_top_k)
   ├─ bm25_store.search(query, bm25_top_k)
   └─ rrf.reciprocal_rank_fusion() → List[RetrievedDoc]
   ↓
4. ContextAssembler.build_prompt_context():
   - Format chunks with [filename] headers
   - Respect MAX_CONTEXT_TOKENS budget
   → formatted_context
   ↓
5. ContextAssembler.build_full_prompt():
   - Combine system + context + query
   → complete_prompt
   ↓
6. LocalLLMWrapper.generate_response():
   - Ollama API call with RAG_SYSTEM_PROMPT
   → answer_text
   ↓
7. Build QueryResponse:
   - answer: answer_text
   - sources: List[SourceRef] with scores + routes
   - query: original query
   ↓
8. Return QueryResponse to API → JSON to client
```

---

## Storage Structure

```
.
├── .chroma/                   # ChromaDB persistent storage
│   ├── chroma.sqlite3         # Metadata DB
│   └── [index files]          # HNSW index
│
├── .bm25/                     # BM25 storage
│   ├── bm25_index.pkl         # Pickled BM25Okapi instance
│   └── chunks.pkl             # Pickled chunks list
│
└── data/
    ├── raw/                   # Original CSV
    └── processed/             # (optional) normalized docs
```

---

## Extending the System

### Add a New Retrieval Method

1. Create `rag/retrieval/new_method.py`
2. Implement `search(query, k) -> List[RetrievedDoc]`
3. Add to `hybrid.py` fusion logic
4. Update RRF to handle 3+ input lists

### Add a New Embedding Model

1. Update `rag/llm/ollama_wrapper.py`
2. Change `OLLAMA_EMBED_MODEL` in `.env`
3. Or implement custom embeddings class

### Add Chat History

1. Extend `QueryRequest` with `history: List[Message]`
2. Modify `build_full_prompt()` to include chat context
3. Update `generate_response()` to pass message history

---

## Performance Considerations

### Latency Breakdown (Typical)

```
Query Processing (~2-5s total):
  - Embedding query:        0.1s
  - Vector search:          0.05s
  - BM25 search:            0.02s
  - RRF fusion:             0.001s
  - Context assembly:       0.001s
  - LLM generation:         1-4s (depends on output length)
```

### Optimization Strategies

1. **Cache embeddings** - Store query embeddings for frequent questions
2. **Batch processing** - Upload multiple documents at once
3. **Async operations** - Use FastAPI async endpoints
4. **GPU acceleration** - Use CUDA/Metal for faster Ollama inference
5. **Smaller chunks** - Reduce embedding time, but may hurt context quality
6. **Quantized models** - Use GGUF quantization for faster inference

---

## Summary

| Component | File | Purpose |
|-----------|------|---------|
| **API Layer** | `rag/api/rag.py` | REST endpoints |
| **Orchestrator** | `rag/core/service.py` | Coordinates pipeline |
| **Ingestion** | `rag/ingestion/ingest.py` | Parse, chunk, embed |
| **Vector Store** | `rag/retrieval/chroma.py` | Semantic search |
| **BM25 Store** | `rag/retrieval/bm25.py` | Keyword search |
| **RRF Fusion** | `rag/retrieval/rrf.py` | Merge rankings |
| **Hybrid Retrieval** | `rag/retrieval/hybrid.py` | Combine vector + BM25 |
| **Context Assembly** | `rag/assembler/context.py` | Build prompts |
| **LLM Wrapper** | `rag/llm/ollama_wrapper.py` | Ollama integration |
| **Prompts** | `rag/prompts/system.py` | System instructions |
| **Types** | `rag/types.py` | Data models |
| **Config** | `rag/config.py` | Settings management |

---

**For parameter tuning, see:** [PARAMETERS.md](PARAMETERS.md)

**For troubleshooting, see:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md)


