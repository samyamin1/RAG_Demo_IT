"""ChromaDB vector store wrapper."""

import os
from typing import List, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from rag.types import Chunk, RetrievedDoc
from rag.config import settings
from rag.llm.ollama_wrapper import OllamaEmbeddings


class ChromaVectorStore:
    """Vector store using ChromaDB."""
    
    def __init__(self, persist_directory: Optional[str] = None):
        """
        Initialize ChromaDB client.
        
        Args:
            persist_directory: Directory to persist the database
        """
        self.persist_directory = persist_directory or settings.chroma_dir
        
        # Ensure directory exists
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True,
            )
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="rag_documents",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Initialize embeddings
        self.embeddings = OllamaEmbeddings()
    
    def add_chunks(
        self,
        chunks: List[Chunk],
        embeddings: List[List[float]],
    ):
        """
        Add chunks with embeddings to the vector store.
        
        Args:
            chunks: List of chunks to add
            embeddings: Corresponding embeddings
        """
        if not chunks:
            return
        
        ids = [chunk.id for chunk in chunks]
        documents = [chunk.content for chunk in chunks]
        metadatas = []
        for chunk in chunks:
            meta = {
                "doc_id": chunk.doc_id,
                "filename": chunk.filename,
                "chunk_index": chunk.chunk_index,
            }
            # Add other metadata but filter out lists (ChromaDB doesn't accept them)
            for key, value in chunk.metadata.items():
                if not isinstance(value, (list, dict)) and value is not None:
                    meta[key] = value
                elif isinstance(value, list):
                    # Convert lists to comma-separated strings
                    meta[key] = ",".join(str(v) for v in value) if value else ""
            metadatas.append(meta)
        
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )
    
    def similarity_search(
        self,
        query: str,
        k: Optional[int] = None,
    ) -> List[RetrievedDoc]:
        """
        Search for similar chunks using vector similarity.
        
        Args:
            query: Query text
            k: Number of results to return
            
        Returns:
            List of retrieved documents with scores
        """
        if k is None:
            k = settings.vector_top_k
        
        # Get query embedding
        query_embedding = self.embeddings.embed_query(query)
        
        # Query ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
        )
        
        # Convert to RetrievedDoc
        retrieved = []
        if results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                doc = RetrievedDoc(
                    id=results['ids'][0][i],
                    doc_id=results['metadatas'][0][i]['doc_id'],
                    filename=results['metadatas'][0][i]['filename'],
                    content=results['documents'][0][i],
                    score=1.0 - results['distances'][0][i],  # Convert distance to similarity
                    route="vector",
                    chunk_index=results['metadatas'][0][i].get('chunk_index'),
                )
                retrieved.append(doc)
        
        return retrieved
    
    def delete_document(self, doc_id: str):
        """
        Delete all chunks of a document.
        
        Args:
            doc_id: Document ID to delete
        """
        # Query for all chunks of this document
        results = self.collection.get(
            where={"doc_id": doc_id}
        )
        
        if results['ids']:
            self.collection.delete(ids=results['ids'])
    
    def count(self) -> int:
        """Get total number of chunks in the store."""
        return self.collection.count()
    
    def reset(self):
        """Clear all data from the vector store."""
        self.client.reset()
        self.collection = self.client.get_or_create_collection(
            name="rag_documents",
            metadata={"hnsw:space": "cosine"}
        )


