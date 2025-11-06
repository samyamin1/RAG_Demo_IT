# Project Structure

Complete overview of the RAG Module file organization.

## Directory Tree

```
RAG/
│
├── rag/                              # Core library
│   ├── __init__.py
│   ├── types.py                      # Pydantic models
│   ├── config.py                     # Settings management
│   │
│   ├── api/                          # FastAPI REST API
│   │   ├── __init__.py
│   │   └── rag.py                    # Endpoints: /upload, /query, /delete, /health
│   │
│   ├── core/                         # Orchestration
│   │   ├── __init__.py
│   │   └── service.py                # CentralizedRAGService
│   │
│   ├── ingestion/                    # Document processing
│   │   ├── __init__.py
│   │   └── ingest.py                 # parse_file, split_text, embed_chunks
│   │
│   ├── retrieval/                    # Hybrid search
│   │   ├── __init__.py
│   │   ├── chroma.py                 # ChromaDB vector store
│   │   ├── bm25.py                   # BM25 lexical search
│   │   ├── hybrid.py                 # DocumentRetrievalService
│   │   └── rrf.py                    # Reciprocal Rank Fusion
│   │
│   ├── assembler/                    # Prompt building
│   │   ├── __init__.py
│   │   └── context.py                # ContextAssembler
│   │
│   ├── llm/                          # Ollama integration
│   │   ├── __init__.py
│   │   └── ollama_wrapper.py         # LocalLLMWrapper, OllamaEmbeddings
│   │
│   └── prompts/                      # System prompts
│       ├── __init__.py
│       └── system.py                 # RAG_SYSTEM_PROMPT, chat templates
│
├── scripts/                          # Utility scripts
│   ├── __init__.py
│   ├── bootstrap.sh                  # One-command setup
│   ├── check_ollama.py               # Verify Ollama & pull model
│   ├── fetch_kaggle_dataset.py       # Prepare dataset
│   ├── index_documents.py            # Build indices
│   ├── demo_wrong_right.py           # Wrong→Right demo
│   ├── wipe_indices.py               # Clear indices
│   ├── eval_grid.py                  # Parameter grid search
│   └── verify_setup.py               # Setup verification
│
├── tests/                            # Test suite
│   ├── __init__.py
│   ├── test_rrf.py                   # RRF fusion tests
│   ├── test_retrieval.py             # Retrieval component tests
│   └── test_api.py                   # API endpoint tests
│
├── data/                             # Data storage
│   ├── raw/                          # Original CSV
│   │   ├── .gitkeep
│   │   └── rag_sample_qas_from_kis.csv  (user-provided)
│   └── processed/                    # Processed docs (optional)
│       └── .gitkeep
│
├── .chroma/                          # ChromaDB vector store (generated)
├── .bm25/                            # BM25 index files (generated)
├── .venv/                            # Virtual environment (generated)
│
├── docs/                             # Documentation
│   └── (optional mkdocs structure)
│
├── .env                              # Environment config (user creates from env.example)
├── env.example                       # Example configuration
├── .gitignore                        # Git ignore patterns
│
├── requirements.txt                  # Python dependencies
├── Makefile                          # Development targets
├── pytest.ini                        # Pytest configuration
├── mkdocs.yml                        # MkDocs config
├── LICENSE                           # MIT License
│
└── Documentation Files:
    ├── README.md                     # Main overview
    ├── QUICK_START.md                # 5-minute guide
    ├── RAG_Kickoff_and_Run.md        # Complete setup guide
    ├── ARCHITECTURE.md               # System architecture
    ├── PARAMETERS.md                 # Parameter tuning guide ⭐
    ├── TROUBLESHOOTING.md            # Common issues
    ├── EVAL_AND_TUNING.md            # Evaluation guide
    ├── CONTRIBUTING.md               # Contribution guidelines
    └── PROJECT_STRUCTURE.md          # This file
```

## File Counts

- **Core library**: 18 Python files
- **Scripts**: 8 utility scripts
- **Tests**: 3 test files
- **Documentation**: 9 markdown files
- **Configuration**: 5 config files

**Total lines of code**: ~4,500 (estimated)

## Key Files by Function

### Configuration
- `env.example` - Default configuration template
- `.env` - User configuration (created from example)
- `rag/config.py` - Settings management with Pydantic

### Orchestration
- `rag/core/service.py` - Main RAG service orchestrating all components
- `rag/api/rag.py` - FastAPI endpoints for external access

### Data Processing
- `rag/ingestion/ingest.py` - Document parsing, chunking, embedding
- `rag/retrieval/hybrid.py` - Hybrid retrieval coordination
- `rag/assembler/context.py` - Prompt building from retrieved docs

### Search Components
- `rag/retrieval/chroma.py` - Vector similarity search (ChromaDB)
- `rag/retrieval/bm25.py` - Keyword search (BM25Okapi)
- `rag/retrieval/rrf.py` - Reciprocal Rank Fusion algorithm

### LLM Integration
- `rag/llm/ollama_wrapper.py` - Ollama client for generation & embeddings
- `rag/prompts/system.py` - System prompts and chat templates

### Utilities
- `scripts/bootstrap.sh` - Automated setup
- `scripts/index_documents.py` - Index builder
- `scripts/demo_wrong_right.py` - Demonstration script
- `scripts/verify_setup.py` - Setup verification

### Documentation
- `README.md` - Project overview and quick reference
- `PARAMETERS.md` - ⭐ Essential parameter tuning guide
- `RAG_Kickoff_and_Run.md` - Complete installation and usage
- `ARCHITECTURE.md` - Detailed system architecture
- `TROUBLESHOOTING.md` - Problem-solving guide

## Generated Files (Not in Git)

These are created during setup/runtime:

```
.chroma/               # ChromaDB vector store
  ├── chroma.sqlite3   # Metadata database
  └── [index files]    # HNSW index data

.bm25/                 # BM25 index storage
  ├── bm25_index.pkl   # Pickled BM25Okapi instance
  └── chunks.pkl       # Pickled chunks list

.venv/                 # Python virtual environment
  ├── bin/             # Executables
  ├── lib/             # Installed packages
  └── ...

.env                   # User configuration (from env.example)

eval_results.json      # Grid search results (if run)
```

## Import Patterns

### Common Imports

```python
# Configuration
from rag.config import settings

# Types
from rag.types import Document, Chunk, RetrievedDoc, QueryResponse

# Core service
from rag.core.service import CentralizedRAGService

# Individual components
from rag.ingestion.ingest import DocumentIngestionService
from rag.retrieval.hybrid import DocumentRetrievalService
from rag.llm.ollama_wrapper import LocalLLMWrapper
```

### Example Usage

```python
# Initialize service
from rag.core.service import CentralizedRAGService
rag = CentralizedRAGService()

# Upload document
result = rag.upload_document(
    content="RAG combines retrieval with generation.",
    filename="intro.txt"
)

# Query
response = rag.query_with_answer("What is RAG?")
print(response.answer)
```

## Component Dependencies

```
FastAPI Application (rag.api.rag)
    ↓
CentralizedRAGService (rag.core.service)
    ↓
    ├─→ DocumentIngestionService (rag.ingestion.ingest)
    │       └─→ OllamaEmbeddings (rag.llm.ollama_wrapper)
    │
    ├─→ DocumentRetrievalService (rag.retrieval.hybrid)
    │       ├─→ ChromaVectorStore (rag.retrieval.chroma)
    │       ├─→ BM25Store (rag.retrieval.bm25)
    │       └─→ RRF (rag.retrieval.rrf)
    │
    ├─→ ContextAssembler (rag.assembler.context)
    │
    └─→ LocalLLMWrapper (rag.llm.ollama_wrapper)
```

## Testing Structure

```
tests/
├── test_rrf.py           # Unit tests for RRF fusion
├── test_retrieval.py     # Integration tests for retrieval
└── test_api.py           # API endpoint tests
```

Run with:
```bash
make test
# or
pytest -v
```

## Documentation Structure

### For Users

1. **QUICK_START.md** - Get running in 5 minutes
2. **README.md** - Overview and quick reference
3. **RAG_Kickoff_and_Run.md** - Complete setup guide
4. **PARAMETERS.md** ⭐ - How to tune for better results
5. **TROUBLESHOOTING.md** - Common problems and solutions

### For Developers

1. **ARCHITECTURE.md** - System design and components
2. **EVAL_AND_TUNING.md** - Evaluation and benchmarking
3. **CONTRIBUTING.md** - Development guidelines
4. **PROJECT_STRUCTURE.md** - This file

### Reference

- **LICENSE** - MIT License
- **requirements.txt** - Python dependencies
- **Makefile** - Build targets
- **pytest.ini** - Test configuration
- **mkdocs.yml** - Documentation site config

## Key Design Patterns

1. **Separation of Concerns**: Each module has a single responsibility
2. **Dependency Injection**: Services accept dependencies in __init__
3. **Configuration Management**: Centralized in `rag/config.py`
4. **Type Safety**: Pydantic models for all data structures
5. **Error Handling**: Try/except with meaningful error messages
6. **Modularity**: Easy to swap components (e.g., different retrievers)

## Extension Points

Want to customize? These are the main extension points:

1. **New Retrieval Method**: Add to `rag/retrieval/`
2. **Custom Embeddings**: Modify `rag/llm/ollama_wrapper.py`
3. **Different Chunking**: Update `rag/ingestion/ingest.py`
4. **Custom Prompts**: Edit `rag/prompts/system.py`
5. **Additional Endpoints**: Extend `rag/api/rag.py`
6. **New Metrics**: Modify `scripts/eval_grid.py`

---

**For architectural details, see:** [ARCHITECTURE.md](ARCHITECTURE.md)

**For development guide, see:** [CONTRIBUTING.md](CONTRIBUTING.md)


