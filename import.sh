#!/bin/bash
# Script per avviare l'import interattivo
# Mostra un menu per scegliere quale file importare

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Attiva l'ambiente virtuale se presente
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi

# Avvia lo script senza argomenti -> modalità interattiva
python3 import_articoli_to_sqlite.py
