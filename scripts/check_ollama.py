"""Check Ollama installation and pull model if needed."""

import sys
import os
import subprocess
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.config import settings
from rag.llm.ollama_wrapper import LocalLLMWrapper


def check_ollama_installed() -> bool:
    """Check if Ollama is installed."""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def print_install_instructions():
    """Print OS-specific Ollama installation instructions."""
    print("\n" + "="*60)
    print("OLLAMA NOT FOUND")
    print("="*60)
    print("\nPlease install Ollama:")
    print("\n  macOS/Linux:")
    print("    curl -fsSL https://ollama.com/install.sh | sh")
    print("\n  Windows:")
    print("    Download from: https://ollama.com/download/windows")
    print("\n  Or visit: https://ollama.com/download")
    print("="*60 + "\n")


def main():
    """Main check and pull logic."""
    print("\n" + "="*60)
    print("CHECKING OLLAMA INSTALLATION")
    print("="*60)
    
    # Check if Ollama is installed
    if not check_ollama_installed():
        print_install_instructions()
        sys.exit(1)
    
    print(f"✓ Ollama is installed")
    print(f"\nChecking model: {settings.ollama_model}")
    
    # Check if model is available
    try:
        llm = LocalLLMWrapper()
        if llm.check_available():
            print(f"✓ Model {settings.ollama_model} is already available")
        else:
            print(f"⚠ Model {settings.ollama_model} not found")
            print(f"Pulling model {settings.ollama_model}...")
            llm.pull_model()
            print(f"✓ Model {settings.ollama_model} pulled successfully")
    
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("OLLAMA CHECK COMPLETE")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()


