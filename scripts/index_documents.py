"""Index documents from the Kaggle dataset into ChromaDB and BM25."""

import sys
import argparse
import pandas as pd
from pathlib import Path
from tqdm import tqdm

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.core.service import CentralizedRAGService
from rag.config import settings, print_config


def load_dataset(csv_path: str) -> pd.DataFrame:
    """Load dataset from CSV."""
    print(f"\nLoading dataset from: {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"[OK] Loaded {len(df)} rows")
    return df


def index_documents(csv_path: str, rebuild: bool = False, limit: int = None):
    """Index documents from CSV into RAG system."""
    print("\n" + "="*60)
    print("INDEXING DOCUMENTS")
    print("="*60)
    
    print_config()
    
    # Initialize RAG service
    rag_service = CentralizedRAGService()
    
    # Reset if rebuild
    if rebuild:
        print("\n[WARNING] Resetting indices...")
        rag_service.reset_indices()
        print("[OK] Indices reset\n")
    
    # Load dataset
    df = load_dataset(csv_path)
    
    # Apply limit if specified
    if limit:
        print(f"[WARNING] Limiting to first {limit} documents")
        df = df.head(limit)
    
    # Index each row
    print(f"\nIndexing {len(df)} documents...")
    
    total_chunks = 0
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Indexing"):
        # Extract fields (adjust based on actual CSV structure)
        # Expected columns: id, title, body/content, tags, source
        doc_id = str(row.get('id', idx))
        title = str(row.get('title', f"Document {idx}"))
        
        # Try different content column names
        content = None
        for col in ['content', 'body', 'text', 'answer', 'response']:
            if col in row and pd.notna(row[col]):
                content = str(row[col])
                break
        
        if not content:
            # Fallback: combine all text columns
            content = " ".join([str(v) for v in row.values if pd.notna(v)])
        
        # Combine title and content
        full_content = f"{title}\n\n{content}"
        
        # Extract metadata
        metadata = {
            'title': title,
            'tags': str(row.get('tags', '')).split(',') if 'tags' in row else [],
            'source': str(row.get('source', 'kaggle_dataset')),
        }
        
        # Upload document
        result = rag_service.upload_document(
            content=full_content,
            filename=f"doc_{doc_id}.csv",
            doc_id=doc_id,
            metadata=metadata,
        )
        
        total_chunks += result['chunks_created']
    
    # Get final status
    status = rag_service.get_status()
    
    print("\n" + "="*60)
    print("INDEXING COMPLETE")
    print("="*60)
    print(f"Documents indexed:   {len(df)}")
    print(f"Total chunks:        {total_chunks}")
    print(f"Vector store count:  {status['vector_chunks']}")
    print(f"BM25 store count:    {status['bm25_chunks']}")
    print("="*60 + "\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Index documents into RAG system")
    parser.add_argument(
        '--csv',
        type=str,
        default='data/raw/rag_sample_qas_from_kis.csv',
        help='Path to CSV dataset'
    )
    parser.add_argument(
        '--rebuild',
        action='store_true',
        help='Reset indices before indexing'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Limit number of documents to index'
    )
    
    args = parser.parse_args()
    
    csv_path = Path(args.csv)
    if not csv_path.exists():
        print(f"[ERROR] CSV file not found: {csv_path}")
        print(f"\nPlease run: python scripts/fetch_kaggle_dataset.py")
        sys.exit(1)
    
    index_documents(str(csv_path), args.rebuild, args.limit)


if __name__ == "__main__":
    main()


