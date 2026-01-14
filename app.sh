#!/bin/bash
# Script per avviare l'applicazione unificata Import & Esplora Articoli
# Mostra un menu principale per scegliere tra importazione e esplorazione
#
# Uso:
#   ./app.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Attiva l'ambiente virtuale se presente
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "⚠️  Virtual environment non trovato!"
    echo ""
    echo "Creazione virtual environment e installazione dipendenze..."
    python3 -m venv .venv
    
    if [ $? -ne 0 ]; then
        echo "❌ Errore: impossibile creare il virtual environment"
        echo "   Installa python3-venv: sudo apt install python3-venv"
        exit 1
    fi
    
    source .venv/bin/activate
    pip install -r requirements.txt
    echo ""
    echo "✅ Virtual environment creato e dipendenze installate!"
    echo ""
fi

# Avvia il launcher unificato (menu principale)
python3 importa_articoli_app.py
