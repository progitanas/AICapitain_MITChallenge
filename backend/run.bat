@echo off
REM Script de lancement du serveur AI Captain (Windows)

setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║         AI CAPTAIN - Maritime Route Optimization                ║
echo ║                     Backend Launch Script                       ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Vérifier que Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installé ou non accessible
    pause
    exit /b 1
)

REM Vérifier que venv existe
if not exist "venv" (
    echo ⚠️  Virtual environment not found. Creating...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activer venv
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Installer/mettre à jour dépendances
echo 📦 Installing dependencies...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

REM Lancer le serveur
echo.
echo ✓ Environment ready
echo.
echo 🚀 Starting AI Captain Backend...
echo.
echo 📍 API Documentation: http://localhost:8000/api/v1/docs
echo 📍 ReDoc: http://localhost:8000/api/v1/redoc
echo 📍 Health Check: http://localhost:8000/health
echo.
echo ⏸️  Press Ctrl+C to stop the server
echo.

python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

pause
