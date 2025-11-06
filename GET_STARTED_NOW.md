# 🚀 GET STARTED NOW - Step-by-Step Guide

**Follow these steps IN ORDER to get RAG running on your Windows machine.**

---

## ✅ Step 1: Install Python (if not installed)

### Check if Python is installed:

Open PowerShell or Command Prompt and type:
```cmd
python --version
```

**If you see "Python 3.11" or higher** → Skip to Step 2

**If you get an error** → Install Python:

1. Go to: https://www.python.org/downloads/
2. Click "Download Python 3.11.x" (or latest 3.11+)
3. Run the installer
4. **⚠️ IMPORTANT**: Check these boxes:
   - ✅ "Add python.exe to PATH"
   - ✅ "Install pip"
5. Click "Install Now"
6. After installation, **close and reopen** your terminal
7. Verify: `python --version`

---

## ✅ Step 2: Install Ollama

### Download and Install:

1. Go to: https://ollama.com/download/windows
2. Download "OllamaSetup.exe"
3. Run the installer
4. Ollama will start automatically (you'll see it in system tray)

### Verify Ollama:

```cmd
ollama --version
```

You should see: `ollama version is ...`

### Pull the Model:

```cmd
ollama pull llama3:8b
```

This will download ~4.7GB. **Wait for it to complete.**

**Note:** If you have less than 8GB RAM, use a smaller model:
```cmd
ollama pull mistral:7b
```

---

## ✅ Step 3: Run the Setup Script

### Open Command Prompt or PowerShell

Navigate to the RAG folder:
```cmd
cd "C:\Users\smami\Downloads\AI Consultations\InnovaDigits\RAG"
```

### Run the Windows Launcher:

**Simply double-click:** `run_rag_windows.bat`

**Or from command line:**
```cmd
run_rag_windows.bat
```

### You'll see a menu. Follow these options IN ORDER:

1. **Option 1**: Auto-Configure
   - This detects your system and creates optimal .env settings
   - Answer "yes" when prompted

2. **Option 2**: Check Ollama and Pull Model
   - Verifies Ollama is running and model is ready

3. **Option 3**: Index Documents
   - Builds the search indices
   - **This takes 5-10 minutes** - be patient!
   - You'll see progress and "INDEXING COMPLETE" at the end

4. **Option 4**: Run Medical Use Case Demo
   - **This is the best demo!**
   - Shows clear difference between Ollama alone vs RAG+Ollama
   - Wait for it to complete

5. **Option 6**: Start API Server
   - Starts the web API
   - Keep this window open
   - Open browser to: http://127.0.0.1:8000/docs

---

## ✅ Step 4: See the Results!

### Medical Demo (Best for seeing clear differences)

When you run **Option 4** (Medical Use Case Demo), you'll see:

```
❌ APPROACH 1: Ollama ALONE
   Generic answer based on training data
   No sources, may be outdated/wrong

✅ APPROACH 2: RAG + Ollama
   Specific answer with citations
   Sources: [doc_023.csv], [doc_045.csv]
   Verifiable and accurate
```

**The difference will be OBVIOUS:**
- Without RAG: Generic, potentially wrong
- With RAG: Specific, cited, accurate

---

## ✅ Step 5: Use the API

### Start the API Server

From the menu: **Option 6** - Start API Server

Or manually:
```cmd
python -m uvicorn rag.api.rag:app --reload --host 127.0.0.1 --port 8000
```

### Test it in your browser:

Open: http://127.0.0.1:8000/docs

You'll see interactive API documentation. Try:

1. Click on `/health` → "Try it out" → "Execute"
2. Click on `/query` → "Try it out"
3. Enter query: `"What is retrieval augmented generation?"`
4. Click "Execute"
5. See the answer with citations!

---

## 🎯 What You'll See

### Before RAG (Ollama Alone):
```
Question: What is the treatment for chronic migraines?

Answer: Chronic migraines are typically treated with...
[Generic answer, no specific citations, may be outdated]

Sources: None
Confidence: Unknown
```

### After RAG (RAG + Ollama):
```
Question: What is the treatment for chronic migraines?

Answer: According to [medical_guidelines_2024.csv], the current
treatment protocol for chronic migraines includes... 
[doc_therapy_options.csv] further notes that...

Sources:
  1. [medical_guidelines_2024.csv] (score: 0.8472, route: hybrid)
  2. [doc_therapy_options.csv] (score: 0.7891, route: vector)
  3. [clinical_trials_2023.csv] (score: 0.7234, route: bm25)

Confidence: High (verified from knowledge base)
```

**The difference is NIGHT and DAY! ✨**

---

## 🔧 Troubleshooting

### "Python not found"
→ Install Python (Step 1) and make sure "Add to PATH" is checked

### "Ollama not found"
→ Install Ollama (Step 2) from https://ollama.com/download/windows

### "Model not found"
→ Run: `ollama pull llama3:8b`

### "Indexing failed"
→ Make sure `rag_sample_qas_from_kis.csv` is in the project folder

### "Out of memory"
→ Close other applications
→ Or use smaller model: `ollama pull mistral:7b` and edit .env to use `OLLAMA_MODEL=mistral:7b`

### "API won't start"
→ Port 8000 might be in use. Try port 8080:
```cmd
python -m uvicorn rag.api.rag:app --reload --port 8080
```

---

## 📊 System Requirements

### Minimum (Will work but slower):
- CPU: 4 cores
- RAM: 8GB
- Disk: 10GB free
- Model: `mistral:7b`

### Recommended (Good performance):
- CPU: 8 cores
- RAM: 16GB
- Disk: 15GB free
- Model: `llama3:8b`

### Optimal (Best performance):
- CPU: 16+ cores
- RAM: 32GB+
- Disk: 20GB+ free
- GPU: NVIDIA GPU with CUDA
- Model: `llama3:8b` or `llama3:70b` if you have 64GB+ RAM

---

## 🎓 Understanding the Results

### Key Metrics in Output:

**Score (0.0 - 1.0):**
- > 0.8: Highly relevant
- 0.6 - 0.8: Relevant
- < 0.6: Marginally relevant

**Route:**
- `vector`: Found via semantic similarity
- `bm25`: Found via keyword matching
- `hybrid`: Combined from both (best!)

**Sources:**
- Shows which documents the answer came from
- You can verify the answer by checking these files

---

## 🎉 Success Indicators

You'll know it's working when:

1. ✅ Medical demo shows cited answers (not generic)
2. ✅ API returns `{"status": "ok", "indices_loaded": true}`
3. ✅ Sources list shows relevant documents with high scores
4. ✅ Answers include [filename] citations
5. ✅ Difference between "without RAG" and "with RAG" is obvious

---

## 📖 Next Steps

After you get it running:

1. **Try your own questions**
   - Use the API or run custom queries
   
2. **Tune parameters** (if needed)
   - Read [PARAMETERS.md](PARAMETERS.md)
   - Edit `.env` file
   - Restart API

3. **Add your own documents**
   - Use the `/upload` API endpoint
   - Or add to CSV and re-index

4. **Integrate into your application**
   - Use the REST API endpoints
   - Or import Python library directly

---

## 💡 Pro Tips

1. **Always keep Ollama running** (check system tray)
2. **Use the medical demo** to see clearest differences
3. **Check .env settings** - auto-configure optimizes for your machine
4. **Monitor RAM usage** - close other apps if needed
5. **Give indexing time** - don't interrupt it!

---

## 🆘 Need Help?

1. **Quick fixes**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. **Windows specific**: See [WINDOWS_SETUP.md](WINDOWS_SETUP.md)
3. **Verify setup**: Run **Option 8** from the menu
4. **Full reset**: Delete `.chroma`, `.bm25`, `.venv` folders and start over

---

## 🎯 QUICK START CHECKLIST

- [ ] Python 3.11+ installed (`python --version`)
- [ ] Ollama installed (`ollama --version`)
- [ ] Model pulled (`ollama pull llama3:8b`)
- [ ] Ran `run_rag_windows.bat`
- [ ] Auto-configured (Option 1)
- [ ] Indexed documents (Option 3) - **wait for completion!**
- [ ] Ran medical demo (Option 4) - **see the difference!**
- [ ] Started API (Option 6)
- [ ] Tested in browser (http://127.0.0.1:8000/docs)

---

**Ready? Let's go!** 🚀

**Start here:** Double-click `run_rag_windows.bat`


