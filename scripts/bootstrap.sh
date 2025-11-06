#!/bin/bash
# Bootstrap script for RAG system setup

set -e

echo "======================================================================"
echo "                    RAG SYSTEM BOOTSTRAP"
echo "======================================================================"

# Check Python version
echo ""
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.11"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)"; then
    echo "✗ Error: Python 3.11+ required (found $python_version)"
    exit 1
fi
echo "✓ Python $python_version"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source .venv/Scripts/activate
else
    source .venv/bin/activate
fi
echo "✓ Virtual environment activated"

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "✓ pip upgraded"

# Install requirements
echo ""
echo "Installing requirements..."
pip install -r requirements.txt
echo "✓ Requirements installed"

# Check Ollama
echo ""
echo "Checking Ollama..."
if command -v ollama &> /dev/null; then
    echo "✓ Ollama found"
    python scripts/check_ollama.py
else
    echo "⚠ Ollama not found!"
    echo ""
    echo "Please install Ollama:"
    echo "  macOS/Linux: curl -fsSL https://ollama.com/install.sh | sh"
    echo "  Windows: https://ollama.com/download/windows"
fi

# Prepare dataset
echo ""
echo "Preparing dataset..."
python scripts/fetch_kaggle_dataset.py

# Create .env if not exists
echo ""
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << 'EOF'
# Ollama Configuration
OLLAMA_MODEL=llama3:8b
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_EMBED_MODEL=nomic-embed-text

# Storage Directories
CHROMA_DIR=.chroma
BM25_DIR=.bm25
DATA_DIR=data

# Retrieval Parameters
TOP_K=5
VECTOR_TOP_K=10
BM25_TOP_K=20
RRF_K=60

# BM25 Parameters
BM25_K1=1.5
BM25_B=0.75

# Chunking Parameters
CHUNK_SIZE=800
CHUNK_OVERLAP=120
SPLITTER=recursive

# LLM Generation Parameters
TEMPERATURE=0.2
MAX_CONTEXT_TOKENS=6000
MAX_OUTPUT_TOKENS=1024

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Evaluation
EVAL_EPOCHS=3
EOF
    echo "✓ .env file created"
else
    echo "✓ .env file already exists"
fi

# Index documents
echo ""
echo "Indexing documents..."
python scripts/index_documents.py --rebuild

echo ""
echo "======================================================================"
echo "                  BOOTSTRAP COMPLETE!"
echo "======================================================================"
echo ""
echo "Next steps:"
echo "  1. Start API:  make run"
echo "  2. Run demo:   make demo"
echo "  3. Run tests:  make test"
echo ""
echo "API docs will be available at: http://localhost:8000/docs"
echo "======================================================================"


