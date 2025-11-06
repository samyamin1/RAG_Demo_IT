"""Hybrid retrieval combining vector and BM25 search."""

from typing import List, Optional
from rag.types import Chunk, RetrievedDoc
from rag.retrieval.chroma import ChromaVectorStore
from rag.retrieval.bm25 import BM25Store
from rag.retrieval.rrf import reciprocal_rank_fusion
from rag.config import settings


class DocumentRetrievalService:
    """Hybrid retrieval service combining vector and BM25 search."""
    
    def __init__(
        self,
        chroma_dir: Optional[str] = None,
        bm25_dir: Optional[str] = None,
    ):
        """
        Initialize hybrid retrieval service.
        
        Args:
            chroma_dir: ChromaDB persist directory
            bm25_dir: BM25 persist directory
        """
        self.vector_store = ChromaVectorStore(persist_directory=chroma_dir)
        self.bm25_store = BM25Store(persist_directory=bm25_dir)
    
    def add_chunks(
        self,
        chunks: List[Chunk],
        embeddings: List[List[float]],
    ):
        """
        Add chunks to both vector and BM25 stores.
        
        Args:
            chunks: List of chunks
            embeddings: Corresponding embeddings
        """
        self.vector_store.add_chunks(chunks, embeddings)
        self.bm25_store.add_chunks(chunks)
    
    def query_documents(
        self,
        query: str,
        top_k: Optional[int] = None,
        vector_top_k: Optional[int] = None,
        bm25_top_k: Optional[int] = None,
        rrf_k: Optional[int] = None,
    ) -> List[RetrievedDoc]:
        """
        Query documents using hybrid search with RRF fusion.
        
        Args:
            query: Query text
            top_k: Number of final results after fusion
            vector_top_k: Number of vector results before fusion
            bm25_top_k: Number of BM25 results before fusion
            rrf_k: RRF constant for fusion
            
        Returns:
            Fused and ranked results
        """
        # Get vector results
        vector_results = self.vector_store.similarity_search(
            query,
            k=vector_top_k or settings.vector_top_k
        )
        
        # Get BM25 results
        bm25_results = self.bm25_store.search(
            query,
            k=bm25_top_k or settings.bm25_top_k
        )
        
        # Fuse with RRF
        fused_results = reciprocal_rank_fusion(
            vector_results,
            bm25_results,
            k=rrf_k or settings.rrf_k,
            top_k=top_k or settings.top_k,
        )
        
        return fused_results
    
    def hybrid_search(
        self,
        query: str,
        top_k: Optional[int] = None,
    ) -> List[RetrievedDoc]:
        """
        Alias for query_documents.
        
        Args:
            query: Query text
            top_k: Number of results
            
        Returns:
            Retrieved documents
        """
        return self.query_documents(query, top_k=top_k)
    
    def delete_document(self, doc_id: str):
        """
        Delete document from both stores.
        
        Args:
            doc_id: Document ID to delete
        """
        self.vector_store.delete_document(doc_id)
        self.bm25_store.delete_document(doc_id)
    
    def count(self) -> dict:
        """Get counts from both stores."""
        return {
            "vector": self.vector_store.count(),
            "bm25": self.bm25_store.count(),
        }
    
    def reset(self):
        """Clear both stores."""
        self.vector_store.reset()
        self.bm25_store.reset()


