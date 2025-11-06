# Contributing to RAG Module

Thank you for your interest in contributing! This document provides guidelines for contributing to the RAG module.

## Getting Started

1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/RAG.git
   cd RAG
   ```
3. **Set up development environment**
   ```bash
   bash scripts/bootstrap.sh
   ```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Changes

- Follow existing code structure
- Add type hints to all functions
- Use Pydantic models for data validation
- Keep functions focused and small

### 3. Add Tests

```bash
# Add tests to tests/ directory
# Test your changes
make test
```

### 4. Update Documentation

- Update relevant `.md` files
- Add docstrings to new functions
- Update PARAMETERS.md if adding new configuration

### 5. Run Quality Checks

```bash
# Run tests
make test

# Check code works end-to-end
make demo

# Verify API
make run
# Test endpoints at http://localhost:8000/docs
```

## Code Style

### Python Style

- Follow PEP 8
- Use descriptive variable names
- Maximum line length: 100 characters
- Use `snake_case` for functions and variables
- Use `PascalCase` for classes

### Example

```python
from typing import List, Optional
from rag.types import Document, Chunk

class MyNewService:
    """Service for doing something useful."""
    
    def __init__(self, config: Optional[dict] = None):
        """Initialize service with optional config."""
        self.config = config or {}
    
    def process_data(self, items: List[str]) -> List[Document]:
        """
        Process list of items into documents.
        
        Args:
            items: List of item strings
            
        Returns:
            List of Document objects
        """
        documents = []
        for item in items:
            doc = self._create_document(item)
            documents.append(doc)
        return documents
    
    def _create_document(self, item: str) -> Document:
        """Private helper to create document."""
        # Implementation
        pass
```

## Project Structure

When adding new features, follow the existing structure:

```
rag/
├── api/              # FastAPI endpoints
├── core/             # Core orchestration
├── ingestion/        # Document processing
├── retrieval/        # Search components
├── assembler/        # Prompt building
├── llm/              # LLM wrappers
├── prompts/          # System prompts
├── types.py          # Data models
└── config.py         # Configuration

scripts/              # Utility scripts
tests/                # Test suite
docs/                 # Documentation
```

## Adding New Features

### Example: Add a New Retrieval Method

1. **Create module**: `rag/retrieval/new_method.py`

   ```python
   from typing import List
   from rag.types import RetrievedDoc
   
   class NewMethodStore:
       def search(self, query: str, k: int) -> List[RetrievedDoc]:
           """Search using new method."""
           # Implementation
           pass
   ```

2. **Integrate**: Update `rag/retrieval/hybrid.py`

   ```python
   from rag.retrieval.new_method import NewMethodStore
   
   class DocumentRetrievalService:
       def __init__(self):
           # ... existing stores ...
           self.new_method_store = NewMethodStore()
   ```

3. **Update RRF**: Modify `rag/retrieval/rrf.py` to handle 3+ input lists

4. **Add tests**: Create `tests/test_new_method.py`

5. **Document**: Update `ARCHITECTURE.md` and `PARAMETERS.md`

## Testing Guidelines

### Unit Tests

- Test individual functions/classes in isolation
- Use pytest fixtures for setup
- Mock external dependencies

### Integration Tests

- Test full pipelines (upload → query)
- Use temporary directories for indices
- Clean up after tests

### Example Test

```python
import pytest
from rag.retrieval.bm25 import BM25Store
from rag.types import Chunk

@pytest.fixture
def sample_chunks():
    return [
        Chunk(
            id="chunk_1",
            doc_id="doc_1",
            content="Test content",
            chunk_index=0,
            filename="test.txt",
            metadata={}
        )
    ]

def test_bm25_search(tmp_path, sample_chunks):
    """Test BM25 search returns results."""
    store = BM25Store(persist_directory=str(tmp_path))
    store.add_chunks(sample_chunks)
    
    results = store.search("test", k=5)
    
    assert len(results) > 0
    assert results[0].route == "bm25"
```

## Documentation

### Docstring Format

```python
def function_name(param1: str, param2: int = 5) -> bool:
    """
    Short description.
    
    Longer description if needed. Explain what the function does,
    why it exists, and any important details.
    
    Args:
        param1: Description of param1
        param2: Description of param2 (default: 5)
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param1 is empty
        RuntimeError: When operation fails
        
    Example:
        >>> function_name("test", 10)
        True
    """
    # Implementation
```

### Updating Documentation

When adding features:
- Update `README.md` if it's user-facing
- Update `ARCHITECTURE.md` for new components
- Update `PARAMETERS.md` for new configuration
- Update `TROUBLESHOOTING.md` for new issues

## Pull Request Process

1. **Update documentation**
2. **Add/update tests**
3. **Ensure all tests pass**: `make test`
4. **Update CHANGELOG** (if exists)
5. **Submit PR** with clear description:

   ```markdown
   ## Description
   Brief description of changes
   
   ## Motivation
   Why is this change needed?
   
   ## Changes
   - Change 1
   - Change 2
   
   ## Testing
   How was this tested?
   
   ## Checklist
   - [ ] Tests added/updated
   - [ ] Documentation updated
   - [ ] All tests pass
   ```

## Code Review

Reviewers will check:
- ✅ Code quality and style
- ✅ Test coverage
- ✅ Documentation completeness
- ✅ Backward compatibility
- ✅ Performance implications

## Questions?

- Review existing code for examples
- Check [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- Read [PARAMETERS.md](PARAMETERS.md) for configuration
- See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues

## License

By contributing, you agree that your contributions will be licensed under the MIT License.


