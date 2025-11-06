# RAG Module - Production-Ready Retrieval Augmented Generation

A fully local, production-ready RAG (Retrieval Augmented Generation) system powered by **Ollama**, featuring **hybrid retrieval** (vector + BM25), **RRF fusion**, and comprehensive **citation support**.

## 🪟 **WINDOWS USERS - START HERE!**

**→ [YOUR_NEXT_STEPS.md](YOUR_NEXT_STEPS.md)** - Complete Windows setup guide

**→ [GET_STARTED_NOW.md](GET_STARTED_NOW.md)** - Step-by-step instructions

**→ Just run:** `run_rag_windows.bat` (double-click!)

---

## 🎯 Overview

This RAG module implements a complete retrieval-augmented generation pipeline that:

- ✅ Runs **100% locally** via Ollama (no API keys required)
- ✅ Uses **hybrid retrieval** (ChromaDB vector search + BM25 lexical search)
- ✅ Implements **Reciprocal Rank Fusion (RRF)** for optimal result merging
- ✅ Provides **cited answers** with source references
- ✅ Offers a **FastAPI REST API** for easy integration
- ✅ Includes **wrong→right demos** showing RAG vs baseline

## 🏗️ Architecture

```
User Query
    ↓
CentralizedRAGService (Orchestration Layer)
    ↓
    ├─→ Document Ingestion Service
    │       ├─ parse_file()
    │       ├─ split_text()
    │       └─ embed_chunks()
    │
    ├─→ Document Retrieval Service (Hybrid)
    │       ├─ Vector Search (ChromaDB)
    │       ├─ BM25 Search (Lexical)
    │       └─ RRF Fusion
    │
    ├─→ Context Assembler
    │       └─ build_prompt_context()
    │
    └─→ LocalLLMWrapper (Ollama)
            └─ generate_response()
                ↓
            QueryResponse (Answer + Sources)
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed component breakdown.

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Ollama** ([install guide](https://ollama.com/download))

### Installation

#### Option 1: Bootstrap Script (Recommended)

```bash
# One-command setup
bash scripts/bootstrap.sh
```

#### Option 2: Manual Setup

```bash
# 1. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Pull Ollama model
ollama pull llama3:8b

# 4. Prepare dataset
python scripts/fetch_kaggle_dataset.py

# 5. Index documents
python scripts/index_documents.py --rebuild
```

### Run the Demo

```bash
# Show "Wrong→Right" comparison
make demo
# or
python scripts/demo_wrong_right.py
```

### Start the API

```bash
make run
# or
uvicorn rag.api.rag:app --reload
```

Visit http://localhost:8000/docs for interactive API documentation.

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [RAG_Kickoff_and_Run.md](RAG_Kickoff_and_Run.md) | **Complete setup and usage guide** |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System architecture and component details |
| [PARAMETERS.md](PARAMETERS.md) | **Parameter tuning guide** (essential!) |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Common issues and solutions |
| [EVAL_AND_TUNING.md](EVAL_AND_TUNING.md) | Evaluation and grid search |

## 🎮 Usage Examples

### Python API

```python
from rag.core.service import CentralizedRAGService

# Initialize service
rag = CentralizedRAGService()

# Upload a document
rag.upload_document(
    content="RAG combines retrieval with LLMs for better answers.",
    filename="intro.txt"
)

# Query with citations
response = rag.query_with_answer("What is RAG?")
print(response.answer)
for source in response.sources:
    print(f"  - {source.filename} (score: {source.score:.3f})")
```

### REST API

```bash
# Upload document
curl -X POST "http://localhost:8000/upload" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "RAG improves LLM accuracy with retrieval.",
    "filename": "rag_info.txt"
  }'

# Query
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How does RAG improve accuracy?",
    "top_k": 5
  }'
```

## 🔑 Key Features

### 1. Hybrid Retrieval

Combines the strengths of two retrieval approaches:

- **Vector Search** (ChromaDB): Semantic similarity via embeddings
- **BM25** (Lexical): Keyword-based ranking
- **RRF Fusion**: Merges results using reciprocal rank fusion

### 2. Citation-Based Answers

All answers cite specific source documents:

```
According to [doc_023.csv], retrieval augmented generation...
```

### 3. Configurable Parameters

Fine-tune every aspect via environment variables or CLI:

```bash
TOP_K=6 CHUNK_SIZE=600 TEMPERATURE=0.1 make run
```

See [PARAMETERS.md](PARAMETERS.md) for the complete tuning guide.

### 4. Wrong→Right Demo

Visual demonstration of RAG's impact:

- **Without RAG**: May hallucinate or provide outdated info
- **With RAG**: Grounded answers with source citations

## 📊 Parameter Tuning

Key parameters for optimal performance:

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `TOP_K` | 5 | Final number of retrieved chunks |
| `VECTOR_TOP_K` | 10 | Vector candidates before fusion |
| `BM25_TOP_K` | 20 | BM25 candidates before fusion |
| `RRF_K` | 60 | RRF fusion dampening factor |
| `CHUNK_SIZE` | 800 | Tokens per chunk |
| `TEMPERATURE` | 0.2 | LLM sampling temperature |

**Read [PARAMETERS.md](PARAMETERS.md) for detailed tuning strategies!**

## 🧪 Testing

```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_rrf.py -v

# Run evaluation grid search
make eval
```

## 📁 Project Structure

```
.
├── rag/                          # Core library
│   ├── api/rag.py                # FastAPI endpoints
│   ├── core/service.py           # CentralizedRAGService
│   ├── ingestion/ingest.py       # Document processing
│   ├── retrieval/
│   │   ├── chroma.py             # Vector store
│   │   ├── bm25.py               # Lexical search
│   │   ├── hybrid.py             # Hybrid retrieval
│   │   └── rrf.py                # RRF fusion
│   ├── assembler/context.py      # Prompt building
│   ├── llm/ollama_wrapper.py     # Ollama integration
│   ├── prompts/system.py         # System prompts
│   ├── types.py                  # Pydantic models
│   └── config.py                 # Configuration
├── scripts/
│   ├── bootstrap.sh              # One-command setup
│   ├── index_documents.py        # Build indices
│   ├── demo_wrong_right.py       # Wrong→Right demo
│   └── eval_grid.py              # Parameter evaluation
├── tests/                        # Test suite
├── data/                         # Dataset storage
├── requirements.txt              # Dependencies
├── Makefile                      # Development targets
└── README.md                     # This file
```

## 🛠️ Makefile Targets

```bash
make setup    # Create venv and install dependencies
make ollama   # Verify Ollama and pull model
make data     # Fetch dataset
make index    # Build indices
make run      # Start API server
make demo     # Run wrong→right demo
make test     # Run tests
make eval     # Run parameter evaluation
make clean    # Remove caches and indices
```

## 🔄 Workflow

1. **Index documents** → `make index`
2. **Start API** → `make run`
3. **Upload documents** → POST `/upload`
4. **Query with RAG** → POST `/query`
5. **Get cited answers** ✅

## 🌟 Why This RAG Module?

- ✅ **Production-ready**: Type-safe, tested, documented
- ✅ **Fully local**: No API keys, no cloud dependencies
- ✅ **Hybrid retrieval**: Best of vector + keyword search
- ✅ **Proven architecture**: Based on established patterns
- ✅ **Tunable**: Extensive parameter control
- ✅ **Cited answers**: Transparent source attribution

## 📚 Dataset

This project uses the **Kaggle Sample RAG Knowledge Item Dataset** (CSV format).

Place `rag_sample_qas_from_kis.csv` in the project root, or run:

```bash
python scripts/fetch_kaggle_dataset.py
```

## 🤝 Contributing

Contributions welcome! Please:

1. Follow the existing code structure
2. Add tests for new features
3. Update documentation
4. Run `make test` before submitting

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- Based on patterns from [iamaziz/mini_RAG_LLM](https://github.com/iamaziz/mini_RAG_LLM)
- Uses [Ollama](https://ollama.com) for local LLM inference
- Built with [LangChain](https://langchain.com), [ChromaDB](https://www.trychroma.com/), and [FastAPI](https://fastapi.tiangolo.com/)

---

**Get Started:** [RAG_Kickoff_and_Run.md](RAG_Kickoff_and_Run.md) | **Tune Parameters:** [PARAMETERS.md](PARAMETERS.md) | **API Docs:** http://localhost:8000/docs

