.PHONY: setup ollama data index run demo test docs clean help

help:
	@echo "Available targets:"
	@echo "  make setup    - Create venv and install dependencies"
	@echo "  make ollama   - Verify Ollama and pull model"
	@echo "  make data     - Fetch Kaggle dataset"
	@echo "  make index    - Build Chroma + BM25 indices"
	@echo "  make run      - Start FastAPI server"
	@echo "  make demo     - Run wrong→right demo"
	@echo "  make test     - Run tests"
	@echo "  make docs     - Build documentation"
	@echo "  make eval     - Run evaluation grid search"
	@echo "  make clean    - Remove caches and indices"

setup:
	@echo "Creating virtual environment..."
	python -m venv .venv
	@echo "Activating venv and installing dependencies..."
ifeq ($(OS),Windows_NT)
	.venv\Scripts\pip install --upgrade pip
	.venv\Scripts\pip install -r requirements.txt
else
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt
endif
	@echo "Setup complete! Activate with: source .venv/bin/activate (Linux/Mac) or .venv\\Scripts\\activate (Windows)"

ollama:
	@echo "Verifying Ollama installation..."
ifeq ($(OS),Windows_NT)
	.venv\Scripts\python scripts/check_ollama.py
else
	.venv/bin/python scripts/check_ollama.py
endif

data:
	@echo "Fetching dataset..."
ifeq ($(OS),Windows_NT)
	.venv\Scripts\python scripts/fetch_kaggle_dataset.py
else
	.venv/bin/python scripts/fetch_kaggle_dataset.py
endif

index:
	@echo "Building indices..."
ifeq ($(OS),Windows_NT)
	.venv\Scripts\python scripts/index_documents.py --rebuild
else
	.venv/bin/python scripts/index_documents.py --rebuild
endif

run:
	@echo "Starting FastAPI server..."
ifeq ($(OS),Windows_NT)
	.venv\Scripts\uvicorn rag.api.rag:app --reload --host 0.0.0.0 --port 8000
else
	.venv/bin/uvicorn rag.api.rag:app --reload --host 0.0.0.0 --port 8000
endif

demo:
	@echo "Running wrong→right demo..."
ifeq ($(OS),Windows_NT)
	.venv\Scripts\python scripts/demo_wrong_right.py
else
	.venv/bin/python scripts/demo_wrong_right.py
endif

test:
	@echo "Running tests..."
ifeq ($(OS),Windows_NT)
	.venv\Scripts\pytest -q
else
	.venv/bin/pytest -q
endif

docs:
	@echo "Building documentation..."
ifeq ($(OS),Windows_NT)
	.venv\Scripts\mkdocs build
else
	.venv/bin/mkdocs build
endif

eval:
	@echo "Running evaluation..."
ifeq ($(OS),Windows_NT)
	.venv\Scripts\python scripts/eval_grid.py
else
	.venv/bin/python scripts/eval_grid.py
endif

clean:
	@echo "Cleaning up..."
	rm -rf .chroma .bm25 __pycache__ .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "Clean complete!"


