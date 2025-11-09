#!/bin/bash
# Script de lancement du serveur AI Captain (Linux/Mac)

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         AI CAPTAIN - Maritime Route Optimization                ║"
echo "║                   Backend Launch Script                         ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.9+"
    exit 1
fi

# Créer venv si nécessaire
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Creating..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
fi

# Activer venv
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Installer dépendances
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "✓ Environment ready"
echo ""
echo "🚀 Starting AI Captain Backend..."
echo ""
echo "📍 API Documentation: http://localhost:8000/api/v1/docs"
echo "📍 ReDoc: http://localhost:8000/api/v1/redoc"
echo "📍 Health Check: http://localhost:8000/health"
echo ""
echo "⏸️  Press Ctrl+C to stop the server"
echo ""

python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
