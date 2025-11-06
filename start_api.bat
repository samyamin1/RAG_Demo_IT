@echo off
REM Start RAG API Server

cd /d "C:\Users\smami\Downloads\AI Consultations\InnovaDigits\RAG"

echo.
echo ========================================================================
echo                        STARTING RAG API SERVER
echo ========================================================================
echo.

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Start server
echo Starting FastAPI server...
echo.
echo API will be available at:
echo   - Interactive Docs: http://127.0.0.1:8000/docs
echo   - Health Check:     http://127.0.0.1:8000/health
echo   - API Root:         http://127.0.0.1:8000
echo.
echo Press CTRL+C to stop the server
echo.
echo ========================================================================
echo.

python -m uvicorn rag.api.rag:app --reload --host 127.0.0.1 --port 8000

pause

