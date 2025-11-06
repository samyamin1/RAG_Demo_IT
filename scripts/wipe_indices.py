"""Wipe all indices and start fresh."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.core.service import CentralizedRAGService


def wipe_indices():
    """Wipe all indices."""
    print("\n" + "="*60)
    print("WIPING INDICES")
    print("="*60)
    print("\n⚠ WARNING: This will delete all indexed documents!")
    
    response = input("\nAre you sure? (yes/no): ")
    if response.lower() != 'yes':
        print("Cancelled.")
        return
    
    print("\nResetting indices...")
    rag_service = CentralizedRAGService()
    rag_service.reset_indices()
    
    print("\n" + "="*60)
    print("INDICES WIPED")
    print("="*60)
    print("\nTo re-index documents, run:")
    print("  python scripts/index_documents.py --rebuild")
    print("="*60 + "\n")


if __name__ == "__main__":
    wipe_indices()


