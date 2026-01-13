#!/bin/bash
# Script per avviare l'esplorazione articoli con il virtual environment
#
# Uso:
#   ./esplora.sh [database.db]
#
# Esempio:
#   ./esplora.sh              # Usa articoli.db di default
#   ./esplora.sh mio_db.db    # Usa database specificato

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Non richiedere all'utente il percorso del DB: usiamo il launcher in modalità Export

# Verifica se esiste il virtual environment
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
    pip install python-docx htmldocx beautifulsoup4
    echo ""
    echo "✅ Virtual environment creato e dipendenze installate!"
    echo ""
fi

# Verifica se esiste il database di default
if [ ! -f "articoli.db" ]; then
    echo "❌ Database 'articoli.db' non trovato!"
    echo ""
    echo "Usa prima lo script di importazione (o posiziona il DB nella cartella):"
    echo "   ./import.sh"
    exit 1
fi

# Avvia il launcher in modalità Export (non chiede il DB)
python importa_articoli_app.py export
