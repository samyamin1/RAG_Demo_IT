"""
Medical Use Case Demo: Clear Difference Between Ollama Alone vs RAG+Ollama

This demo uses medical/technical questions where:
- WITHOUT RAG: LLM gives generic, potentially outdated, or wrong information
- WITH RAG: LLM gives specific, cited, accurate information from the knowledge base
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.core.service import CentralizedRAGService
from rag.llm.ollama_wrapper import LocalLLMWrapper
from rag.prompts.system import GENERIC_NO_CONTEXT_SYSTEM_PROMPT
from rag.config import settings, print_config


# Medical/Technical Use Case Questions
MEDICAL_DEMO_QUESTIONS = [
    {
        "question": "What is the recommended treatment protocol for chronic migraines according to the latest clinical guidelines?",
        "why_rag_matters": "Generic LLM may give outdated or general advice. RAG provides specific, cited clinical guidelines from knowledge base.",
        "category": "Medical - Clinical Guidelines"
    },
    {
        "question": "What are the contraindications for administering intravenous contrast media in patients with renal impairment?",
        "why_rag_matters": "Safety-critical information that requires precise, cited medical literature. Wrong answer could harm patients.",
        "category": "Medical - Patient Safety"
    },
    {
        "question": "What is the specific coding procedure for billing Medicare Part B claims for telehealth services in rural areas?",
        "why_rag_matters": "Regulatory information that changes frequently. Generic LLM likely has outdated billing codes. RAG cites current regulations.",
        "category": "Medical - Regulatory/Billing"
    },
]


def print_header(text, char="=", width=80):
    """Print formatted header."""
    print("\n" + char * width)
    print(text.center(width))
    print(char * width)


def print_section(text, char="-", width=80):
    """Print formatted section."""
    print("\n" + char * width)
    print(text)
    print(char * width)


def format_sources(sources):
    """Format sources list."""
    if not sources:
        return "  No sources available"
    
    output = []
    for i, src in enumerate(sources, 1):
        output.append(f"  {i}. [{src.filename}]")
        output.append(f"     Score: {src.score:.4f} | Route: {src.route}")
    return "\n".join(output)


def run_medical_demo():
    """Run medical use case demonstration."""
    print_header("MEDICAL USE CASE: RAG vs. Baseline LLM", "=", 80)
    
    print("""
    ╔══════════════════════════════════════════════════════════════════════╗
    ║                                                                      ║
    ║  This demo demonstrates the CRITICAL DIFFERENCE between:            ║
    ║                                                                      ║
    ║  ❌ Ollama ALONE (Baseline)                                         ║
    ║     - Generic knowledge from training                               ║
    ║     - May be outdated or incorrect                                  ║
    ║     - No source citations                                           ║
    ║     - Risk of hallucination                                         ║
    ║                                                                      ║
    ║  ✅ RAG + Ollama (Knowledge-Grounded)                               ║
    ║     - Specific information from your knowledge base                 ║
    ║     - Current and verified                                          ║
    ║     - Cites exact sources                                           ║
    ║     - Grounded in evidence                                          ║
    ║                                                                      ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    print_config()
    
    # Initialize services
    print("\n🔧 Initializing RAG service...")
    rag_service = CentralizedRAGService()
    llm = LocalLLMWrapper()
    
    # Check status
    status = rag_service.get_status()
    if not status['indices_loaded']:
        print("\n⚠️  WARNING: No documents indexed!")
        print("     RAG will not work without indexed documents.")
        print("\n     Run this first:")
        print("     python scripts/index_documents.py --rebuild\n")
        sys.exit(1)
    
    print(f"\n✓ RAG service ready:")
    print(f"  - Ollama: {'✓ Available' if status['ollama_available'] else '✗ Not available'}")
    print(f"  - Model: {status['ollama_model']}")
    print(f"  - Vector chunks: {status['vector_chunks']}")
    print(f"  - BM25 chunks: {status['bm25_chunks']}")
    
    # Run demos
    for i, demo in enumerate(MEDICAL_DEMO_QUESTIONS, 1):
        question = demo["question"]
        category = demo["category"]
        why_matters = demo["why_rag_matters"]
        
        print_header(f"USE CASE {i}: {category}", "=", 80)
        
        print(f"\n📋 QUESTION:")
        print(f"   {question}")
        
        print(f"\n💡 WHY RAG MATTERS:")
        print(f"   {why_matters}")
        
        # ═══════════════════════════════════════════════════════════
        # PART 1: WITHOUT RAG (Baseline - Ollama Alone)
        # ═══════════════════════════════════════════════════════════
        
        print_section("❌ APPROACH 1: Ollama ALONE (No Retrieval)", "-", 80)
        print("\n⚙️  Mode: Generic LLM using training data only")
        print("⚙️  Context: None")
        print("⚙️  Sources: None")
        
        try:
            print("\n⏳ Generating answer (this may take 5-15 seconds)...")
            answer_no_rag = llm.generate_response(
                prompt=f"Question: {question}\n\nProvide a clear, concise answer.",
                system_prompt=GENERIC_NO_CONTEXT_SYSTEM_PROMPT,
                temperature=0.2,
            )
            
            print(f"\n📝 ANSWER:")
            print("─" * 80)
            print(answer_no_rag)
            print("─" * 80)
            
            print(f"\n⚠️  LIMITATIONS:")
            print("   • No source citations")
            print("   • Based on training data (may be outdated)")
            print("   • Cannot verify accuracy")
            print("   • May hallucinate specific details")
            print("   • Generic, not tailored to your knowledge base")
            
        except Exception as e:
            print(f"\n✗ Error generating baseline answer: {str(e)}")
            print("   (This might happen if Ollama is not running)")
        
        # ═══════════════════════════════════════════════════════════
        # PART 2: WITH RAG (RAG + Ollama)
        # ═══════════════════════════════════════════════════════════
        
        print_section("✅ APPROACH 2: RAG + Ollama (Retrieval-Augmented)", "-", 80)
        print("\n⚙️  Mode: Hybrid Retrieval + Generation")
        print("⚙️  Context: Retrieved from knowledge base")
        print("⚙️  Sources: Cited with confidence scores")
        
        try:
            print("\n⏳ Retrieving relevant documents...")
            print("   • Vector search (semantic similarity)")
            print("   • BM25 search (keyword matching)")
            print("   • RRF fusion (combining results)")
            
            print("\n⏳ Generating answer with context...")
            response = rag_service.query_with_answer(question)
            
            print(f"\n📝 ANSWER:")
            print("─" * 80)
            print(response.answer)
            print("─" * 80)
            
            print(f"\n📚 SOURCES ({len(response.sources)} documents):")
            print(format_sources(response.sources))
            
            print(f"\n✅ ADVANTAGES:")
            print("   • Specific citations from knowledge base")
            print("   • Evidence-based answer")
            print("   • Verifiable (you can check sources)")
            print("   • Current information from your documents")
            print("   • Transparent about source of information")
            
            # Analysis
            print(f"\n📊 RETRIEVAL ANALYSIS:")
            routes = {}
            for src in response.sources:
                routes[src.route] = routes.get(src.route, 0) + 1
            
            print(f"   • Total sources: {len(response.sources)}")
            for route, count in routes.items():
                print(f"   • {route.capitalize()} matches: {count}")
            
            if response.sources:
                avg_score = sum(s.score for s in response.sources) / len(response.sources)
                max_score = max(s.score for s in response.sources)
                print(f"   • Average confidence: {avg_score:.4f}")
                print(f"   • Highest confidence: {max_score:.4f}")
            
        except Exception as e:
            print(f"\n✗ Error generating RAG answer: {str(e)}")
        
        # Comparison Summary
        print_section("🎯 COMPARISON SUMMARY", "=", 80)
        print("""
        ┌──────────────────────┬─────────────────────┬──────────────────────┐
        │ Aspect               │ Ollama Alone ❌     │ RAG + Ollama ✅      │
        ├──────────────────────┼─────────────────────┼──────────────────────┤
        │ Source Citations     │ None                │ Specific documents   │
        │ Accuracy             │ Unknown             │ Verifiable           │
        │ Recency              │ Training cutoff     │ Your current data    │
        │ Hallucination Risk   │ Higher              │ Lower (grounded)     │
        │ Trust                │ Must take on faith  │ Can verify sources   │
        │ Specificity          │ Generic             │ Tailored to your KB  │
        └──────────────────────┴─────────────────────┴──────────────────────┘
        """)
        
        if i < len(MEDICAL_DEMO_QUESTIONS):
            input("\n⏸  Press ENTER to continue to next use case...")
    
    # Final Summary
    print_header("FINAL SUMMARY: Why RAG Matters", "=", 80)
    print("""
    🎯 KEY TAKEAWAYS:
    
    1. ACCURACY & TRUST
       • RAG provides verifiable, cited information
       • You can trace every claim back to a specific source
       • Critical for medical, legal, financial domains
    
    2. CURRENT INFORMATION
       • LLM training data has a cutoff date
       • RAG uses YOUR current documents
       • Always up-to-date with your knowledge base
    
    3. REDUCED HALLUCINATION
       • LLM alone may "make up" plausible-sounding but wrong facts
       • RAG grounds answers in actual retrieved documents
       • Admits when information is not in the knowledge base
    
    4. DOMAIN SPECIFICITY
       • Generic LLM has broad but shallow knowledge
       • RAG provides deep, specific knowledge from your documents
       • Tailored to YOUR organization's information
    
    5. TRANSPARENCY
       • RAG shows WHERE information comes from
       • Enables fact-checking and validation
       • Builds user trust and confidence
    
    ═══════════════════════════════════════════════════════════════════════
    
    🏥 FOR MEDICAL USE CASES:
       • Patient safety requires verifiable, current information
       • Regulatory compliance demands cited sources
       • Malpractice risk reduced with evidence-based answers
       • Clinical guidelines change—RAG keeps you current
    
    ⚖️  FOR LEGAL USE CASES:
       • Case law and precedents must be cited accurately
       • Regulations change—RAG provides current versions
       • Discovery requires traceable sources
       • Liability reduced with documented sources
    
    💼 FOR BUSINESS USE CASES:
       • Company policies and procedures must be current
       • Compliance requirements demand accuracy
       • Audit trails require source documentation
       • Competitive intelligence needs verified facts
    
    ═══════════════════════════════════════════════════════════════════════
    """)
    
    print("\n✅ Demo Complete!")
    print("\n📖 Next Steps:")
    print("   1. Review the configuration in .env")
    print("   2. Tune parameters (see PARAMETERS.md)")
    print("   3. Start the API: python -m uvicorn rag.api.rag:app --reload")
    print("   4. Try your own questions!")
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    try:
        run_medical_demo()
    except KeyboardInterrupt:
        print("\n\n⏹  Demo interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n✗ Demo failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


