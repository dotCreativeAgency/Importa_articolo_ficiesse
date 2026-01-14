#!/usr/bin/env bash
set -euo pipefail
# Build a one-file executable with PyInstaller (Legacy script)
# RECOMMENDED: Use ./build.sh instead for full environment management
# Usage: ./scripts/build_windows.sh

echo "⚠️  DEPRECATO: Usa ./build.sh per gestione completa dell'ambiente"
echo "Procedendo con build semplice..."
echo ""

# Verifica che PyInstaller sia disponibile
if ! command -v pyinstaller &> /dev/null; then
    echo "❌ PyInstaller non trovato. Installa con:"
    echo "   pip install -r requirements-dev.txt"
    exit 1
fi

pyinstaller --onefile --name importa_articoli importa_articoli_app.py

if [ -f "dist/importa_articoli" ]; then
    echo ""
    echo "✅ Build completato: dist/importa_articoli"
    echo "💡 Per build completo usa: ./build.sh"
else
    echo "❌ Errore: build fallito"
    exit 1
fi