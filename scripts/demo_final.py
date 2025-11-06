"""Final working demo using actual dataset content."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.core.service import CentralizedRAGService
from rag.llm.ollama_wrapper import LocalLLMWrapper
from rag.prompts.system import GENERIC_NO_CONTEXT_SYSTEM_PROMPT
import pandas as pd

print("\n" + "="*80)
print("RAG DEMONSTRATION: Ollama Alone vs RAG+Ollama")
print("="*80)

# Load questions from dataset
df = pd.read_csv('data/raw/rag_sample_qas_from_kis.csv')
questions = df['sample_question'].head(2).tolist()

# Initialize
print("\nInitializing RAG service...")
rag_service = CentralizedRAGService()
llm = LocalLLMWrapper()

status = rag_service.get_status()
print(f"Ollama: {'OK' if status['ollama_available'] else 'Not Available'}")
print(f"Indexed chunks: {status['vector_chunks']}")

for i, question in enumerate(questions, 1):
    question = question.strip('"')
    
    print("\n" + "="*80)
    print(f"DEMO {i}: {question}")
    print("="*80)
    
    # WITHOUT RAG
    print("\n" + "-"*80)
    print("[WITHOUT RAG] Ollama Baseline")
    print("-"*80)
    
    try:
        answer_no_rag = llm.generate_response(
            prompt=f"Question: {question}\n\nProvide a helpful answer.",
            system_prompt=GENERIC_NO_CONTEXT_SYSTEM_PROMPT,
        )
        print(f"\nAnswer:\n{answer_no_rag}")
        print("\n[Limitations]")
        print("  - No source citations")
        print("  - Generic knowledge only")
        print("  - Cannot verify accuracy")
    except Exception as e:
        print(f"[ERROR] {str(e)}")
    
    # WITH RAG
    print("\n" + "-"*80)
    print("[WITH RAG] RAG + Ollama")
    print("-"*80)
    
    try:
        response = rag_service.query_with_answer(question)
        print(f"\nAnswer:\n{response.answer}")
        
        if response.sources:
            print(f"\n[SOURCES] {len(response.sources)} documents retrieved:")
            for j, src in enumerate(response.sources, 1):
                print(f"  {j}. {src.filename}")
                print(f"     Score: {src.score:.4f} | Route: {src.route}")
            
            print("\n[Advantages]")
            print("  - Citations from knowledge base")
            print("  - Evidence-based answer")
            print("  - Verifiable information")
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")
    
    print("\n" + "="*80)

print("\n" + "="*80)
print("KEY TAKEAWAY:")
print("="*80)
print("WITHOUT RAG: Generic answer from training data")
print("WITH RAG:    Specific answer citing your documents")
print("\nThis shows RAG grounds answers in YOUR knowledge base!")
print("="*80 + "\n")

