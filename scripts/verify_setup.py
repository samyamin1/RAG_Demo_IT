"""Verify RAG system setup and configuration."""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def check_python_version():
    """Check Python version is 3.11+."""
    print("Checking Python version...")
    major, minor = sys.version_info[:2]
    if major >= 3 and minor >= 11:
        print(f"  ✓ Python {major}.{minor}")
        return True
    else:
        print(f"  ✗ Python {major}.{minor} (need 3.11+)")
        return False


def check_dependencies():
    """Check required packages are installed."""
    print("\nChecking dependencies...")
    required = [
        "fastapi",
        "uvicorn",
        "langchain",
        "chromadb",
        "rank_bm25",
        "ollama",
        "pydantic",
    ]
    
    all_ok = True
    for package in required:
        try:
            __import__(package.replace("-", "_"))
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} not found")
            all_ok = False
    
    return all_ok


def check_ollama():
    """Check Ollama installation and model."""
    print("\nChecking Ollama...")
    try:
        from rag.llm.ollama_wrapper import LocalLLMWrapper
        from rag.config import settings
        
        llm = LocalLLMWrapper()
        if llm.check_available():
            print(f"  ✓ Ollama running")
            print(f"  ✓ Model {settings.ollama_model} available")
            return True
        else:
            print(f"  ✗ Model {settings.ollama_model} not found")
            print(f"    Run: ollama pull {settings.ollama_model}")
            return False
    except Exception as e:
        print(f"  ✗ Ollama error: {str(e)}")
        print(f"    Run: ollama serve")
        return False


def check_dataset():
    """Check dataset is present."""
    print("\nChecking dataset...")
    csv_path = Path("data/raw/rag_sample_qas_from_kis.csv")
    root_csv = Path("rag_sample_qas_from_kis.csv")
    
    if csv_path.exists():
        print(f"  ✓ Dataset found at {csv_path}")
        return True
    elif root_csv.exists():
        print(f"  ⚠ Dataset found at root, run: python scripts/fetch_kaggle_dataset.py")
        return True
    else:
        print(f"  ✗ Dataset not found")
        print(f"    Place rag_sample_qas_from_kis.csv in project root")
        return False


def check_indices():
    """Check if indices are built."""
    print("\nChecking indices...")
    try:
        from rag.core.service import CentralizedRAGService
        
        rag = CentralizedRAGService()
        status = rag.get_status()
        
        if status['indices_loaded']:
            print(f"  ✓ Indices loaded")
            print(f"    Vector chunks: {status['vector_chunks']}")
            print(f"    BM25 chunks: {status['bm25_chunks']}")
            return True
        else:
            print(f"  ⚠ Indices empty")
            print(f"    Run: make index")
            return False
    except Exception as e:
        print(f"  ⚠ Could not check indices: {str(e)}")
        print(f"    Run: make index")
        return False


def check_config():
    """Check configuration."""
    print("\nChecking configuration...")
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if env_file.exists():
        print(f"  ✓ .env file exists")
    else:
        if env_example.exists():
            print(f"  ⚠ .env not found, using defaults")
            print(f"    Copy env.example to .env to customize")
        else:
            print(f"  ⚠ No .env file (using defaults)")
    
    try:
        from rag.config import settings
        print(f"  ✓ Configuration loaded")
        print(f"    Model: {settings.ollama_model}")
        print(f"    TOP_K: {settings.top_k}")
        return True
    except Exception as e:
        print(f"  ✗ Config error: {str(e)}")
        return False


def main():
    """Run all checks."""
    print("="*60)
    print("RAG SYSTEM SETUP VERIFICATION")
    print("="*60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Ollama", check_ollama),
        ("Dataset", check_dataset),
        ("Configuration", check_config),
        ("Indices", check_indices),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"\n  ✗ {name} check failed: {str(e)}")
            results[name] = False
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    for name, passed in results.items():
        status = "✓" if passed else "✗"
        print(f"{status} {name}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("✓ ALL CHECKS PASSED")
        print("\nNext steps:")
        print("  - Start API:  make run")
        print("  - Run demo:   make demo")
        print("  - Run tests:  make test")
    else:
        print("✗ SOME CHECKS FAILED")
        print("\nRecommended actions:")
        if not results.get("Dependencies", True):
            print("  1. pip install -r requirements.txt")
        if not results.get("Ollama", True):
            print("  2. ollama serve && ollama pull llama3:8b")
        if not results.get("Dataset", True):
            print("  3. python scripts/fetch_kaggle_dataset.py")
        if not results.get("Indices", True):
            print("  4. make index")
        print("\nOr run full setup:")
        print("  bash scripts/bootstrap.sh")
    print("="*60 + "\n")
    
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()


