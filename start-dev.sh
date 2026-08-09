#!/usr/bin/env bash
set -e

echo "🚀 Starter Lokale Entwicklung für Bergfex Dashboard..."

# 1. Prüfen ob .venv existiert
if [ ! -d ".venv" ]; then
    echo "📦 Erstelle Python .venv..."
    python3 -m venv .venv
fi

# 2. Prüfen ob Uvicorn in .venv installiert ist
if ! .venv/bin/python -c "import uvicorn, fastapi" 2>/dev/null; then
    echo "📥 Installiere Python-Abhängigkeiten in .venv..."
    .venv/bin/pip install -r server/requirements.txt
fi

# 3. Prüfen ob node_modules existieren
if [ ! -d "node_modules" ]; then
    echo "📥 Installiere Node.js-Abhängigkeiten..."
    npm install
fi

# 4. Alte / blockierte Prozesse auf Port 8000 und 8080 beenden (falls noch im Hintergrund aktiv)
PIDS=$(lsof -ti:8000 -ti:8080 2>/dev/null || true)
if [ -n "$PIDS" ]; then
    echo "🧹 Beende alte/blockierte Prozesse auf Port 8000/8080 ($PIDS)..."
    kill -9 $PIDS 2>/dev/null || true
    sleep 1
fi

# 5. Starte Frontend & Backend simultan über npm run dev
echo "✨ Starte Frontend (Vite auf http://localhost:8080) & Backend (FastAPI auf http://localhost:8000)..."
echo "💡 Schließe den Server jederzeit mit Ctrl+C"
echo ""

npm run dev
