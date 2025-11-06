"""BM25 lexical search implementation."""

import os
import pickle
from typing import List, Optional
from rank_bm25 import BM25Okapi
from rag.types import Chunk, RetrievedDoc
from rag.config import settings


class BM25Store:
    """BM25 lexical search using rank_bm25."""
    
    def __init__(self, persist_directory: Optional[str] = None):
        """
        Initialize BM25 store.
        
        Args:
            persist_directory: Directory to persist the index
        """
        self.persist_directory = persist_directory or settings.bm25_dir
        os.makedirs(self.persist_directory, exist_ok=True)
        
        self.index_path = os.path.join(self.persist_directory, "bm25_index.pkl")
        self.chunks_path = os.path.join(self.persist_directory, "chunks.pkl")
        
        self.bm25: Optional[BM25Okapi] = None
        self.chunks: List[Chunk] = []
        
        # Load if exists
        self.load()
    
    def tokenize(self, text: str) -> List[str]:
        """Simple tokenization (can be enhanced)."""
        return text.lower().split()
    
    def add_chunks(self, chunks: List[Chunk]):
        """
        Add chunks to BM25 index.
        
        Args:
            chunks: List of chunks to add
        """
        if not chunks:
            return
        
        self.chunks.extend(chunks)
        
        # Tokenize all documents
        tokenized_corpus = [self.tokenize(chunk.content) for chunk in self.chunks]
        
        # Build BM25 index with custom parameters
        self.bm25 = BM25Okapi(
            tokenized_corpus,
            k1=settings.bm25_k1,
            b=settings.bm25_b,
        )
        
        # Persist
        self.save()
    
    def search(
        self,
        query: str,
        k: Optional[int] = None,
    ) -> List[RetrievedDoc]:
        """
        Search using BM25 scoring.
        
        Args:
            query: Query text
            k: Number of results to return
            
        Returns:
            List of retrieved documents with BM25 scores
        """
        if k is None:
            k = settings.bm25_top_k
        
        if not self.bm25 or not self.chunks:
            return []
        
        # Tokenize query
        tokenized_query = self.tokenize(query)
        
        # Get BM25 scores
        scores = self.bm25.get_scores(tokenized_query)
        
        # Get top-k indices
        top_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )[:k]
        
        # Build results
        results = []
        for idx in top_indices:
            chunk = self.chunks[idx]
            doc = RetrievedDoc(
                id=chunk.id,
                doc_id=chunk.doc_id,
                filename=chunk.filename,
                content=chunk.content,
                score=float(scores[idx]),
                route="bm25",
                chunk_index=chunk.chunk_index,
            )
            results.append(doc)
        
        return results
    
    def delete_document(self, doc_id: str):
        """
        Delete all chunks of a document.
        
        Args:
            doc_id: Document ID to delete
        """
        # Filter out chunks from this document
        self.chunks = [c for c in self.chunks if c.doc_id != doc_id]
        
        # Rebuild index
        if self.chunks:
            tokenized_corpus = [self.tokenize(chunk.content) for chunk in self.chunks]
            self.bm25 = BM25Okapi(
                tokenized_corpus,
                k1=settings.bm25_k1,
                b=settings.bm25_b,
            )
        else:
            self.bm25 = None
        
        self.save()
    
    def count(self) -> int:
        """Get total number of chunks."""
        return len(self.chunks)
    
    def save(self):
        """Persist BM25 index and chunks."""
        with open(self.index_path, 'wb') as f:
            pickle.dump(self.bm25, f)
        with open(self.chunks_path, 'wb') as f:
            pickle.dump(self.chunks, f)
    
    def load(self):
        """Load BM25 index and chunks from disk."""
        if os.path.exists(self.index_path) and os.path.exists(self.chunks_path):
            try:
                with open(self.index_path, 'rb') as f:
                    self.bm25 = pickle.load(f)
                with open(self.chunks_path, 'rb') as f:
                    self.chunks = pickle.load(f)
            except Exception as e:
                print(f"Warning: Could not load BM25 index: {e}")
                self.bm25 = None
                self.chunks = []
    
    def reset(self):
        """Clear all data."""
        self.bm25 = None
        self.chunks = []
        if os.path.exists(self.index_path):
            os.remove(self.index_path)
        if os.path.exists(self.chunks_path):
            os.remove(self.chunks_path)


