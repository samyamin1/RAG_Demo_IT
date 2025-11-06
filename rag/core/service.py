"""CentralizedRAGService - Main orchestration layer."""

from typing import Optional, Dict, Any, List
from rag.types import Document, QueryResponse, SourceRef
from rag.ingestion.ingest import DocumentIngestionService
from rag.retrieval.hybrid import DocumentRetrievalService
from rag.assembler.context import ContextAssembler
from rag.llm.ollama_wrapper import LocalLLMWrapper
from rag.prompts.system import RAG_SYSTEM_PROMPT
from rag.config import settings


class CentralizedRAGService:
    """
    Main RAG orchestration service.
    
    Coordinates: Ingestion → Retrieval → Context Assembly → Generation
    """
    
    def __init__(
        self,
        chroma_dir: Optional[str] = None,
        bm25_dir: Optional[str] = None,
    ):
        """
        Initialize RAG service with all components.
        
        Args:
            chroma_dir: ChromaDB directory
            bm25_dir: BM25 directory
        """
        self.ingestion_service = DocumentIngestionService()
        self.retrieval_service = DocumentRetrievalService(
            chroma_dir=chroma_dir,
            bm25_dir=bm25_dir,
        )
        self.context_assembler = ContextAssembler()
        self.llm = LocalLLMWrapper()
    
    def upload_document(
        self,
        content: str,
        filename: str,
        doc_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Upload and index a document.
        
        Args:
            content: Document text content
            filename: Source filename
            doc_id: Optional document ID
            metadata: Optional metadata
            
        Returns:
            Dict with doc_id, filename, and chunks_created
        """
        # Process document through ingestion pipeline
        document, chunks, embeddings = self.ingestion_service.process_document(
            content=content,
            filename=filename,
            doc_id=doc_id,
            metadata=metadata,
        )
        
        # Add to retrieval indices
        self.retrieval_service.add_chunks(chunks, embeddings)
        
        return {
            "doc_id": document.id,
            "filename": filename,
            "chunks_created": len(chunks),
            "status": "success"
        }
    
    def query_with_answer(
        self,
        query: str,
        top_k: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> QueryResponse:
        """
        Query with retrieval and generate answer.
        
        Args:
            query: User question
            top_k: Number of chunks to retrieve
            temperature: LLM temperature override
            
        Returns:
            QueryResponse with answer and sources
        """
        # Retrieve relevant documents
        retrieved_docs = self.retrieval_service.query_documents(
            query=query,
            top_k=top_k,
        )
        
        # Build context
        context = self.context_assembler.build_prompt_context(
            retrieved_docs=retrieved_docs,
            query=query,
        )
        
        # Build prompt
        prompt = self.context_assembler.build_full_prompt(
            query=query,
            context=context,
            system_prompt=RAG_SYSTEM_PROMPT,
        )
        
        # Generate answer
        answer = self.llm.generate_response(
            prompt=prompt,
            system_prompt=RAG_SYSTEM_PROMPT,
            temperature=temperature,
        )
        
        # Build source references
        sources = [
            SourceRef(
                id=doc.id,
                filename=doc.filename,
                score=doc.score,
                route=doc.route,
            )
            for doc in retrieved_docs
        ]
        
        return QueryResponse(
            answer=answer,
            sources=sources,
            query=query,
        )
    
    def delete_document(self, doc_id: str):
        """
        Delete document from all indices.
        
        Args:
            doc_id: Document ID to delete
        """
        self.retrieval_service.delete_document(doc_id)
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get system status.
        
        Returns:
            Status dict with health info
        """
        counts = self.retrieval_service.count()
        ollama_available = self.llm.check_available()
        
        return {
            "status": "ok" if ollama_available else "degraded",
            "ollama_available": ollama_available,
            "ollama_model": settings.ollama_model,
            "indices_loaded": counts["vector"] > 0 and counts["bm25"] > 0,
            "vector_chunks": counts["vector"],
            "bm25_chunks": counts["bm25"],
        }
    
    def reset_indices(self):
        """Clear all indices (for testing/rebuilding)."""
        self.retrieval_service.reset()


