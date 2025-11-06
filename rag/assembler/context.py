"""Context assembler for building prompts with retrieved documents."""

from typing import List
from rag.types import RetrievedDoc
from rag.config import settings


class ContextAssembler:
    """Builds context from retrieved documents for LLM prompting."""
    
    def __init__(self, max_context_tokens: int = None):
        """
        Initialize context assembler.
        
        Args:
            max_context_tokens: Maximum tokens for context window
        """
        self.max_context_tokens = max_context_tokens or settings.max_context_tokens
    
    def build_prompt_context(
        self,
        retrieved_docs: List[RetrievedDoc],
        query: str,
    ) -> str:
        """
        Build formatted context from retrieved documents.
        
        Format:
        [filename1.csv]
        <content of chunk 1>
        
        [filename2.csv]
        <content of chunk 2>
        
        Args:
            retrieved_docs: List of retrieved documents
            query: Original query (for reference)
            
        Returns:
            Formatted context string
        """
        if not retrieved_docs:
            return ""
        
        # De-duplicate by doc_id and chunk_index
        seen = set()
        unique_docs = []
        for doc in retrieved_docs:
            key = (doc.doc_id, doc.chunk_index)
            if key not in seen:
                seen.add(key)
                unique_docs.append(doc)
        
        # Build context with filename headers
        context_parts = []
        total_length = 0
        
        for doc in unique_docs:
            # Format: [filename]\ncontent\n\n
            header = f"[{doc.filename}]"
            chunk_text = f"{header}\n{doc.content}\n"
            
            # Rough token estimation (chars / 4)
            estimated_tokens = len(chunk_text) // 4
            
            if total_length + estimated_tokens > self.max_context_tokens:
                # Stop adding if we exceed budget
                break
            
            context_parts.append(chunk_text)
            total_length += estimated_tokens
        
        return "\n".join(context_parts)
    
    def build_full_prompt(
        self,
        query: str,
        context: str,
        system_prompt: str,
    ) -> str:
        """
        Build complete prompt with system, context, and query.
        
        Args:
            query: User query
            context: Formatted context from retrieved docs
            system_prompt: System instructions
            
        Returns:
            Complete prompt string
        """
        if context:
            prompt = f"""Based on the following context documents, please answer the question.

CONTEXT:
{context}

QUESTION: {query}

ANSWER:"""
        else:
            prompt = f"""QUESTION: {query}

ANSWER:"""
        
        return prompt
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count (simple heuristic).
        
        Args:
            text: Text to estimate
            
        Returns:
            Estimated token count
        """
        # Rough estimate: 1 token ≈ 4 characters
        return len(text) // 4


