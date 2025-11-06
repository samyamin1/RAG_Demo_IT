"""Test everything is working - Simple verification script."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("\n" + "="*70)
print("RAG SYSTEM - VERIFICATION TEST")
print("="*70)

# Test 1: Imports
print("\n[TEST 1] Testing imports...")
try:
    from rag.core.service import CentralizedRAGService
    from rag.llm.ollama_wrapper import LocalLLMWrapper
    print("  [OK] All imports successful")
except Exception as e:
    print(f"  [FAIL] Import error: {e}")
    sys.exit(1)

# Test 2: Ollama connection
print("\n[TEST 2] Testing Ollama connection...")
try:
    llm = LocalLLMWrapper()
    available = llm.check_available()
    if available:
        print("  [OK] Ollama is running and model is available")
    else:
        print("  [WARNING] Ollama model not found")
        print("  Run: ollama pull llama3:8b")
except Exception as e:
    print(f"  [FAIL] Ollama connection error: {e}")
    print("  Make sure Ollama is running (check system tray)")

# Test 3: Indices loaded
print("\n[TEST 3] Testing indices...")
try:
    rag = CentralizedRAGService()
    status = rag.get_status()
    print(f"  Vector chunks: {status['vector_chunks']}")
    print(f"  BM25 chunks: {status['bm25_chunks']}")
    if status['vector_chunks'] > 0:
        print("  [OK] Indices are loaded")
    else:
        print("  [WARNING] No documents indexed")
        print("  Run: python scripts/index_documents.py --rebuild")
except Exception as e:
    print(f"  [FAIL] Index error: {e}")

# Test 4: Simple query
print("\n[TEST 4] Testing simple query...")
try:
    rag = CentralizedRAGService()
    response = rag.query_with_answer("How do I reset my PIN?", top_k=3)
    print(f"  Answer length: {len(response.answer)} characters")
    print(f"  Sources found: {len(response.sources)}")
    print(f"  [OK] Query successful")
    
    print(f"\n  Answer preview:")
    print(f"  {response.answer[:150]}...")
    
    if response.sources:
        print(f"\n  Top source:")
        src = response.sources[0]
        print(f"    File: {src.filename}")
        print(f"    Score: {src.score:.4f}")
        print(f"    Route: {src.route}")
    
except Exception as e:
    print(f"  [FAIL] Query error: {e}")

# Test 5: FastAPI imports
print("\n[TEST 5] Testing FastAPI availability...")
try:
    from rag.api.rag import app
    print("  [OK] FastAPI app is ready")
    print("  You can start the API with:")
    print("    python -m uvicorn rag.api.rag:app --host 127.0.0.1 --port 8000")
    print("  Or double-click: start_api.bat")
except Exception as e:
    print(f"  [FAIL] FastAPI error: {e}")

print("\n" + "="*70)
print("VERIFICATION COMPLETE")
print("="*70)
print("\nNext steps:")
print("  1. Start API: Double-click start_api.bat")
print("  2. Open browser: http://127.0.0.1:8000/docs")
print("  3. Test queries in Swagger UI")
print("="*70 + "\n")

