"""Simple demo without Unicode characters for Windows compatibility."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.core.service import CentralizedRAGService
from rag.llm.ollama_wrapper import LocalLLMWrapper
from rag.prompts.system import GENERIC_NO_CONTEXT_SYSTEM_PROMPT

print("\n" + "="*80)
print("RAG DEMO: Ollama Alone vs RAG+Ollama")
print("="*80)

# Initialize
print("\nInitializing RAG service...")
rag_service = CentralizedRAGService()
llm = LocalLLMWrapper()

# Check status
status = rag_service.get_status()
print(f"Status: {status['status']}")
print(f"Indexed chunks: {status['vector_chunks']}")

# Demo question
question = "What is retrieval augmented generation and how does it work?"

print("\n" + "="*80)
print(f"QUESTION: {question}")
print("="*80)

# Part 1: Without RAG
print("\n" + "-"*80)
print("[BASELINE] Ollama ALONE (No RAG)")
print("-"*80)

try:
    answer_no_rag = llm.generate_response(
        prompt=f"Question: {question}",
        system_prompt=GENERIC_NO_CONTEXT_SYSTEM_PROMPT,
    )
    print(f"\nAnswer:\n{answer_no_rag}")
    print("\n[INFO] This answer has:")
    print("  - No source citations")
    print("  - Based on training data only")
    print("  - May be outdated or generic")
except Exception as e:
    print(f"[ERROR] {str(e)}")

# Part 2: With RAG
print("\n" + "-"*80)
print("[RAG] Ollama WITH Retrieval")
print("-"*80)

try:
    response = rag_service.query_with_answer(question)
    print(f"\nAnswer:\n{response.answer}")
    print(f"\n[SOURCES] Retrieved {len(response.sources)} documents:")
    for i, src in enumerate(response.sources, 1):
        print(f"  {i}. {src.filename}")
        print(f"     Score: {src.score:.4f} | Route: {src.route}")
    print("\n[INFO] This answer has:")
    print("  - Specific source citations")
    print("  - Grounded in knowledge base")
    print("  - Verifiable and accurate")
except Exception as e:
    print(f"[ERROR] {str(e)}")

print("\n" + "="*80)
print("DEMO COMPLETE")
print("="*80)
print("\nKey Difference:")
print("  WITHOUT RAG: Generic answer, no sources")
print("  WITH RAG: Cited answer from specific documents")
print("\n")

