@echo off
REM ========================================================================
REM RAG System - Windows Launcher
REM ========================================================================

echo.
echo ========================================================================
echo                    RAG SYSTEM - WINDOWS LAUNCHER
echo ========================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.11+ from:
    echo   https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add python.exe to PATH" during installation!
    pause
    exit /b 1
)

echo [OK] Python found: 
python --version
echo.

REM Check if virtual environment exists
if not exist .venv (
    echo [SETUP] Creating virtual environment...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
    echo.
)

REM Activate virtual environment
echo [SETUP] Activating virtual environment...
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment!
    pause
    exit /b 1
)
echo [OK] Virtual environment activated
echo.

REM Install/Update requirements
echo [SETUP] Installing/updating dependencies...
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies!
    pause
    exit /b 1
)
echo [OK] Dependencies installed
echo.

REM Check if Ollama is installed
ollama --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Ollama is not installed!
    echo.
    echo Please install Ollama from:
    echo   https://ollama.com/download/windows
    echo.
    echo After installing, run this script again.
    pause
    exit /b 1
)

echo [OK] Ollama found:
ollama --version
echo.

REM Menu
:MENU
echo.
echo ========================================================================
echo                              MAIN MENU
echo ========================================================================
echo.
echo 1. Auto-Configure (Detect system resources and optimize)
echo 2. Check Ollama and Pull Model
echo 3. Index Documents
echo 4. Run Medical Use Case Demo (Shows RAG vs Baseline)
echo 5. Run Standard Demo
echo 6. Start API Server
echo 7. Run Tests
echo 8. Verify Setup
echo 9. Open API Documentation (Browser)
echo 0. Exit
echo.
set /p choice="Select option (0-9): "

if "%choice%"=="1" goto AUTOCONFIG
if "%choice%"=="2" goto CHECKOLLAMA
if "%choice%"=="3" goto INDEX
if "%choice%"=="4" goto DEMO_MEDICAL
if "%choice%"=="5" goto DEMO_STANDARD
if "%choice%"=="6" goto API
if "%choice%"=="7" goto TESTS
if "%choice%"=="8" goto VERIFY
if "%choice%"=="9" goto DOCS
if "%choice%"=="0" goto END

echo [ERROR] Invalid choice!
goto MENU

:AUTOCONFIG
echo.
echo ========================================================================
echo                        AUTO-CONFIGURATION
echo ========================================================================
echo.
python scripts/auto_configure.py
pause
goto MENU

:CHECKOLLAMA
echo.
echo ========================================================================
echo                       CHECK OLLAMA AND PULL MODEL
echo ========================================================================
echo.
python scripts/check_ollama.py
pause
goto MENU

:INDEX
echo.
echo ========================================================================
echo                          INDEX DOCUMENTS
echo ========================================================================
echo.
echo This will build the ChromaDB and BM25 indices.
echo This may take 5-10 minutes depending on dataset size.
echo.
set /p confirm="Continue? (y/n): "
if /i not "%confirm%"=="y" goto MENU

python scripts/index_documents.py --rebuild
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Indexing failed!
    pause
    goto MENU
)
echo.
echo [OK] Indexing complete!
pause
goto MENU

:DEMO_MEDICAL
echo.
echo ========================================================================
echo                  MEDICAL USE CASE DEMO (RAG vs Baseline)
echo ========================================================================
echo.
echo This demo clearly shows the difference between:
echo   - Ollama ALONE (generic, may be wrong)
echo   - RAG + Ollama (cited, accurate)
echo.
pause

python scripts/demo_medical_usecase.py
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Demo failed! Make sure documents are indexed first.
    echo Run option 3 to index documents.
)
pause
goto MENU

:DEMO_STANDARD
echo.
echo ========================================================================
echo                       STANDARD DEMO
echo ========================================================================
echo.
python scripts/demo_wrong_right.py
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Demo failed! Make sure documents are indexed first.
)
pause
goto MENU

:API
echo.
echo ========================================================================
echo                        START API SERVER
echo ========================================================================
echo.
echo Starting FastAPI server on http://127.0.0.1:8000
echo.
echo API Documentation: http://127.0.0.1:8000/docs
echo Health Check:      http://127.0.0.1:8000/health
echo.
echo Press CTRL+C to stop the server
echo.
python -m uvicorn rag.api.rag:app --reload --host 127.0.0.1 --port 8000
pause
goto MENU

:TESTS
echo.
echo ========================================================================
echo                            RUN TESTS
echo ========================================================================
echo.
pytest -v
pause
goto MENU

:VERIFY
echo.
echo ========================================================================
echo                          VERIFY SETUP
echo ========================================================================
echo.
python scripts/verify_setup.py
pause
goto MENU

:DOCS
echo.
echo ========================================================================
echo                    OPEN API DOCUMENTATION
echo ========================================================================
echo.
echo Opening http://127.0.0.1:8000/docs in browser...
echo.
echo NOTE: Make sure API server is running (option 6)
echo.
start http://127.0.0.1:8000/docs
pause
goto MENU

:END
echo.
echo ========================================================================
echo                            GOODBYE!
echo ========================================================================
echo.
echo Deactivating virtual environment...
call .venv\Scripts\deactivate.bat
echo.
echo Thank you for using RAG System!
echo.
pause
exit /b 0


