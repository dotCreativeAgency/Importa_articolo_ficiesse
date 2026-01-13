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

# Nome del database (default: articoli.db)
DB_NAME="${1:-articoli.db}"

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

# Verifica se esiste il database
if [ ! -f "$DB_NAME" ]; then
    echo "❌ Database '$DB_NAME' non trovato!"
    echo ""
    echo "Usa prima lo script di importazione:"
    echo "   ./run_import.sh t_articoli.sql"
    exit 1
fi

# Avvia l'esplorazione
python esplora_articoli.py "$DB_NAME"
