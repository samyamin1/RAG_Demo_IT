"""Wrong→Right demo: Show LLM without RAG vs with RAG."""

import sys
import random
import pandas as pd
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.core.service import CentralizedRAGService
from rag.llm.ollama_wrapper import LocalLLMWrapper
from rag.prompts.system import GENERIC_NO_CONTEXT_SYSTEM_PROMPT
from rag.config import settings, print_config


def load_sample_questions(csv_path: str, n: int = 2):
    """Load sample questions from dataset."""
    df = pd.read_csv(csv_path)
    
    # Try to find question column
    question_col = None
    for col in ['question', 'query', 'q', 'title']:
        if col in df.columns:
            question_col = col
            break
    
    if question_col:
        questions = df[question_col].dropna().tolist()
    else:
        # Fallback: use titles or first text column
        text_cols = df.select_dtypes(include=['object']).columns
        if len(text_cols) > 0:
            questions = df[text_cols[0]].dropna().tolist()
        else:
            questions = []
    
    # Sample n questions
    if len(questions) >= n:
        return random.sample(questions, n)
    else:
        return questions


def demo_wrong_right():
    """Run wrong→right demonstration."""
    print("\n" + "="*70)
    print(" " * 15 + "WRONG → RIGHT DEMO")
    print("="*70)
    print("\nThis demo shows the difference between:")
    print("  WRONG: LLM without retrieval (may hallucinate)")
    print("  RIGHT: LLM with RAG (cites sources)")
    print("="*70)
    
    print_config()
    
    # Initialize services
    print("\nInitializing RAG service...")
    rag_service = CentralizedRAGService()
    llm = LocalLLMWrapper()
    
    # Check status
    status = rag_service.get_status()
    if not status['indices_loaded']:
        print("\n⚠ Warning: No documents indexed!")
        print("Please run: python scripts/index_documents.py --rebuild")
        print("\nUsing generic demo questions instead...\n")
        questions = [
            "What are the main benefits of retrieval augmented generation?",
            "How does hybrid search combine vector and keyword approaches?"
        ]
    else:
        # Load questions from dataset
        csv_path = Path('data/raw/rag_sample_qas_from_kis.csv')
        if csv_path.exists():
            questions = load_sample_questions(str(csv_path), n=2)
        else:
            questions = [
                "What are the main benefits of retrieval augmented generation?",
                "How does hybrid search combine vector and keyword approaches?"
            ]
    
    # Run demos for each question
    for i, question in enumerate(questions, 1):
        print("\n" + "="*70)
        print(f"DEMO {i}: {question}")
        print("="*70)
        
        # WRONG: Answer without retrieval
        print("\n" + "-"*70)
        print("❌ WITHOUT RAG (Baseline - May Hallucinate)")
        print("-"*70)
        try:
            answer_no_rag = llm.generate_response(
                prompt=f"Question: {question}",
                system_prompt=GENERIC_NO_CONTEXT_SYSTEM_PROMPT,
            )
            print(f"\nAnswer:\n{answer_no_rag}")
            print("\n⚠ Note: This answer is based solely on the model's training data.")
            print("   It may be outdated, incorrect, or hallucinated.")
        except Exception as e:
            print(f"\n✗ Error generating baseline answer: {str(e)}")
        
        # RIGHT: Answer with RAG
        print("\n" + "-"*70)
        print("✅ WITH RAG (Retrieval + Context)")
        print("-"*70)
        try:
            response = rag_service.query_with_answer(question)
            print(f"\nAnswer:\n{response.answer}")
            print(f"\n📚 Sources ({len(response.sources)}):")
            for j, source in enumerate(response.sources, 1):
                print(f"  {j}. {source.filename} (score: {source.score:.3f}, route: {source.route})")
            print("\n✓ This answer is grounded in the knowledge base with citations.")
        except Exception as e:
            print(f"\n✗ Error generating RAG answer: {str(e)}")
        
        print("\n" + "="*70)
    
    print("\n" + "="*70)
    print("DEMO COMPLETE")
    print("="*70)
    print("\nKey Takeaways:")
    print("  • WITHOUT RAG: May hallucinate or provide outdated information")
    print("  • WITH RAG: Cites specific sources, grounded in knowledge base")
    print("  • Hybrid retrieval combines vector similarity + keyword matching")
    print("  • RRF fusion ensures best results from both approaches")
    print("="*70 + "\n")


if __name__ == "__main__":
    demo_wrong_right()


