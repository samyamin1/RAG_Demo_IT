"""
Auto-configuration script for RAG system based on available resources.

Detects CPU, RAM, and GPU, then configures optimal parameters.
"""

import sys
import os
import platform
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def get_system_ram_gb():
    """Get total system RAM in GB."""
    try:
        if platform.system() == "Windows":
            import subprocess
            result = subprocess.run(
                ['wmic', 'computersystem', 'get', 'totalphysicalmemory'],
                capture_output=True,
                text=True
            )
            # Parse output
            lines = result.stdout.strip().split('\n')
            if len(lines) >= 2:
                bytes_ram = int(lines[1].strip())
                return bytes_ram / (1024 ** 3)  # Convert to GB
        else:
            # Linux/Mac
            import subprocess
            result = subprocess.run(['free', '-b'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            for line in lines:
                if line.startswith('Mem:'):
                    bytes_ram = int(line.split()[1])
                    return bytes_ram / (1024 ** 3)
    except Exception as e:
        print(f"⚠ Could not detect RAM: {e}")
        return None
    
    return None


def get_cpu_info():
    """Get CPU information."""
    try:
        if platform.system() == "Windows":
            import subprocess
            result = subprocess.run(
                ['wmic', 'cpu', 'get', 'Name,NumberOfCores,NumberOfLogicalProcessors'],
                capture_output=True,
                text=True
            )
            return result.stdout.strip()
        else:
            import subprocess
            result = subprocess.run(['lscpu'], capture_output=True, text=True)
            return result.stdout.strip()
    except Exception as e:
        return f"Could not detect CPU: {e}"


def check_gpu():
    """Check for NVIDIA GPU (for CUDA acceleration)."""
    try:
        import subprocess
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False


def recommend_model(ram_gb):
    """Recommend Ollama model based on RAM."""
    if ram_gb is None:
        return "llama3:8b", "Unknown RAM, using default"
    
    if ram_gb < 8:
        return "mistral:7b", "Low RAM detected, using smaller model"
    elif ram_gb < 16:
        return "llama3:8b", "Moderate RAM, using standard model"
    elif ram_gb < 32:
        return "llama3:8b", "Good RAM, using standard model"
    else:
        return "llama3:8b", "High RAM, using standard model (or try llama3:70b for even better quality)"


def get_optimal_config(ram_gb, has_gpu):
    """Generate optimal configuration based on system resources."""
    config = {}
    
    if ram_gb is None:
        # Conservative defaults
        config = {
            "OLLAMA_MODEL": "llama3:8b",
            "TOP_K": "5",
            "VECTOR_TOP_K": "10",
            "BM25_TOP_K": "20",
            "RRF_K": "60",
            "CHUNK_SIZE": "800",
            "CHUNK_OVERLAP": "120",
            "TEMPERATURE": "0.2",
            "MAX_CONTEXT_TOKENS": "6000",
            "MAX_OUTPUT_TOKENS": "1024",
            "BM25_K1": "1.5",
            "BM25_B": "0.75",
        }
        return config, "Conservative (unknown RAM)"
    
    # LOW RAM: < 8GB
    if ram_gb < 8:
        config = {
            "OLLAMA_MODEL": "mistral:7b",
            "TOP_K": "3",
            "VECTOR_TOP_K": "6",
            "BM25_TOP_K": "12",
            "RRF_K": "60",
            "CHUNK_SIZE": "500",
            "CHUNK_OVERLAP": "80",
            "TEMPERATURE": "0.2",
            "MAX_CONTEXT_TOKENS": "3000",
            "MAX_OUTPUT_TOKENS": "512",
            "BM25_K1": "1.5",
            "BM25_B": "0.75",
        }
        profile = "LOW_RAM (< 8GB)"
    
    # MODERATE RAM: 8-16GB
    elif ram_gb < 16:
        config = {
            "OLLAMA_MODEL": "llama3:8b",
            "TOP_K": "4",
            "VECTOR_TOP_K": "8",
            "BM25_TOP_K": "16",
            "RRF_K": "60",
            "CHUNK_SIZE": "700",
            "CHUNK_OVERLAP": "100",
            "TEMPERATURE": "0.2",
            "MAX_CONTEXT_TOKENS": "5000",
            "MAX_OUTPUT_TOKENS": "1024",
            "BM25_K1": "1.5",
            "BM25_B": "0.75",
        }
        profile = "MODERATE_RAM (8-16GB)"
    
    # GOOD RAM: 16-32GB
    elif ram_gb < 32:
        config = {
            "OLLAMA_MODEL": "llama3:8b",
            "TOP_K": "5",
            "VECTOR_TOP_K": "10",
            "BM25_TOP_K": "20",
            "RRF_K": "60",
            "CHUNK_SIZE": "800",
            "CHUNK_OVERLAP": "120",
            "TEMPERATURE": "0.2",
            "MAX_CONTEXT_TOKENS": "6000",
            "MAX_OUTPUT_TOKENS": "1024",
            "BM25_K1": "1.5",
            "BM25_B": "0.75",
        }
        profile = "GOOD_RAM (16-32GB)"
    
    # HIGH RAM: 32GB+
    else:
        config = {
            "OLLAMA_MODEL": "llama3:8b",
            "TOP_K": "8",
            "VECTOR_TOP_K": "16",
            "BM25_TOP_K": "30",
            "RRF_K": "60",
            "CHUNK_SIZE": "1000",
            "CHUNK_OVERLAP": "150",
            "TEMPERATURE": "0.2",
            "MAX_CONTEXT_TOKENS": "8000",
            "MAX_OUTPUT_TOKENS": "1536",
            "BM25_K1": "1.5",
            "BM25_B": "0.75",
        }
        profile = "HIGH_RAM (32GB+)"
    
    # Adjust for GPU
    if has_gpu:
        profile += " + GPU"
    
    return config, profile


def create_env_file(config, profile):
    """Create .env file with optimized configuration."""
    env_path = Path(".env")
    
    # Backup existing .env if it exists
    if env_path.exists():
        backup_path = Path(".env.backup")
        import shutil
        shutil.copy(env_path, backup_path)
        print(f"✓ Backed up existing .env to .env.backup")
    
    # Create .env with optimized config
    env_content = f"""# Auto-generated configuration for RAG system
# Profile: {profile}
# Generated: {import_datetime_now()}

# Ollama Configuration
OLLAMA_MODEL={config['OLLAMA_MODEL']}
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_EMBED_MODEL=nomic-embed-text

# Storage Directories
CHROMA_DIR=.chroma
BM25_DIR=.bm25
DATA_DIR=data

# Retrieval Parameters (optimized for your system)
TOP_K={config['TOP_K']}
VECTOR_TOP_K={config['VECTOR_TOP_K']}
BM25_TOP_K={config['BM25_TOP_K']}
RRF_K={config['RRF_K']}

# BM25 Parameters
BM25_K1={config['BM25_K1']}
BM25_B={config['BM25_B']}

# Chunking Parameters (optimized for your RAM)
CHUNK_SIZE={config['CHUNK_SIZE']}
CHUNK_OVERLAP={config['CHUNK_OVERLAP']}
SPLITTER=recursive

# LLM Generation Parameters
TEMPERATURE={config['TEMPERATURE']}
MAX_CONTEXT_TOKENS={config['MAX_CONTEXT_TOKENS']}
MAX_OUTPUT_TOKENS={config['MAX_OUTPUT_TOKENS']}

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Evaluation
EVAL_EPOCHS=3
"""
    
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print(f"✓ Created optimized .env file")


def import_datetime_now():
    """Get current datetime string."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def main():
    """Main auto-configuration routine."""
    print("=" * 80)
    print("RAG SYSTEM AUTO-CONFIGURATION".center(80))
    print("=" * 80)
    
    print("\n🔍 Detecting system resources...\n")
    
    # Detect system info
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {platform.python_version()}")
    
    # RAM
    ram_gb = get_system_ram_gb()
    if ram_gb:
        print(f"RAM: {ram_gb:.1f} GB")
    else:
        print(f"RAM: Could not detect (will use conservative defaults)")
    
    # CPU
    print("\nCPU Info:")
    cpu_info = get_cpu_info()
    if "Could not detect" not in cpu_info:
        print(cpu_info[:200])  # Print first 200 chars
    else:
        print(cpu_info)
    
    # GPU
    has_gpu = check_gpu()
    if has_gpu:
        print("\n✓ NVIDIA GPU detected (CUDA acceleration available)")
    else:
        print("\n○ No NVIDIA GPU detected (CPU only)")
    
    # Generate optimal config
    print("\n" + "=" * 80)
    print("GENERATING OPTIMAL CONFIGURATION")
    print("=" * 80 + "\n")
    
    config, profile = get_optimal_config(ram_gb, has_gpu)
    
    print(f"📊 Selected Profile: {profile}")
    print(f"\n⚙️  Recommended Configuration:\n")
    
    # Display config
    print("┌─────────────────────────┬──────────────┬────────────────────────┐")
    print("│ Parameter               │ Value        │ Reason                 │")
    print("├─────────────────────────┼──────────────┼────────────────────────┤")
    
    recommendations = {
        "OLLAMA_MODEL": {
            "value": config["OLLAMA_MODEL"],
            "reason": "Fits in available RAM"
        },
        "TOP_K": {
            "value": config["TOP_K"],
            "reason": "Final result count"
        },
        "VECTOR_TOP_K": {
            "value": config["VECTOR_TOP_K"],
            "reason": "Vector candidates"
        },
        "BM25_TOP_K": {
            "value": config["BM25_TOP_K"],
            "reason": "Lexical candidates"
        },
        "CHUNK_SIZE": {
            "value": config["CHUNK_SIZE"],
            "reason": "Optimized for RAM"
        },
        "MAX_CONTEXT_TOKENS": {
            "value": config["MAX_CONTEXT_TOKENS"],
            "reason": "Context window budget"
        },
    }
    
    for param, info in recommendations.items():
        print(f"│ {param:23} │ {info['value']:12} │ {info['reason']:22} │")
    
    print("└─────────────────────────┴──────────────┴────────────────────────┘")
    
    # Ask to create .env
    print("\n" + "=" * 80)
    response = input("\n❓ Create .env file with these settings? (yes/no): ").strip().lower()
    
    if response in ['yes', 'y']:
        create_env_file(config, profile)
        print("\n✅ Configuration complete!")
        print("\n📋 Next steps:")
        print("   1. Pull the recommended model:")
        print(f"      ollama pull {config['OLLAMA_MODEL']}")
        print("\n   2. Index documents:")
        print("      python scripts/index_documents.py --rebuild")
        print("\n   3. Run demo:")
        print("      python scripts/demo_medical_usecase.py")
        print("\n   4. Start API:")
        print("      python -m uvicorn rag.api.rag:app --reload")
    else:
        print("\n⏹  Configuration cancelled. You can run this script again anytime.")
        print("\n   To manually configure, copy env.example to .env and edit:")
        if platform.system() == "Windows":
            print("   Copy-Item env.example .env")
        else:
            print("   cp env.example .env")
    
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹  Configuration cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n✗ Configuration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


