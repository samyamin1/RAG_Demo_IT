"""Fetch or prepare the Kaggle dataset."""

import sys
import os
import shutil
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.config import settings


def prepare_dataset():
    """Prepare dataset for RAG system."""
    print("\n" + "="*60)
    print("PREPARING DATASET")
    print("="*60)
    
    data_dir = Path(settings.data_dir)
    raw_dir = data_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if CSV already exists in project root
    root_csv = Path("rag_sample_qas_from_kis.csv")
    target_csv = raw_dir / "rag_sample_qas_from_kis.csv"
    
    if root_csv.exists():
        print(f"[OK] Found dataset in root: {root_csv}")
        if not target_csv.exists():
            print(f"  Copying to: {target_csv}")
            shutil.copy(root_csv, target_csv)
        print(f"[OK] Dataset ready at: {target_csv}")
    elif target_csv.exists():
        print(f"[OK] Dataset already exists at: {target_csv}")
    else:
        print(f"\n[WARNING] Dataset not found!")
        print(f"\nPlease ensure 'rag_sample_qas_from_kis.csv' is in the project root")
        print(f"or in {raw_dir}/")
        print(f"\nDataset source: Kaggle 'Sample RAG Knowledge Item Dataset'")
        print(f"URL: https://www.kaggle.com/datasets/...")
        return False
    
    print("\n" + "="*60)
    print("DATASET PREPARATION COMPLETE")
    print("="*60 + "\n")
    return True


if __name__ == "__main__":
    success = prepare_dataset()
    sys.exit(0 if success else 1)


