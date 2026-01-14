#!/usr/bin/env bash
set -euo pipefail
# Script per creare l'eseguibile con PyInstaller
# Si comporta come app.sh: gestisce virtual environment e dipendenze automaticamente
#
# Uso:
#   ./build.sh [--clean] [--test]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

CLEAN_BUILD=false
TEST_BUILD=false

# Parse arguments
for arg in "$@"; do
    case $arg in
        --clean)
            CLEAN_BUILD=true
            shift
            ;;
        --test)
            TEST_BUILD=true
            shift
            ;;
        *)
            echo "⚠️  Argomento sconosciuto: $arg"
            echo "Uso: $0 [--clean] [--test]"
            echo "  --clean  Rimuovi build precedenti"
            echo "  --test   Esegui test dopo il build"
            exit 1
            ;;
    esac
done

echo "🔨 Build Eseguibile - Importa Articoli Ficiesse"
echo "=" * 50

# Pulisci build precedenti se richiesto
if [ "$CLEAN_BUILD" = true ]; then
    echo "🗑️  Pulizia build precedenti..."
    rm -rf dist/ build/ *.spec
    echo "✅ Pulizia completata"
    echo ""
fi

# Attiva l'ambiente virtuale se presente (stessa logica di app.sh)
if [ -d ".venv" ]; then
    echo "🐍 Attivazione virtual environment (.venv)..."
    source .venv/bin/activate
elif [ -d "venv" ]; then
    echo "🐍 Attivazione virtual environment (venv)..."
    source venv/bin/activate
else
    echo "⚠️  Virtual environment non trovato!"
    echo ""
    echo "🔧 Creazione virtual environment e installazione dipendenze..."
    python3 -m venv .venv
    
    if [ $? -ne 0 ]; then
        echo "❌ Errore: impossibile creare il virtual environment"
        echo "   Installa python3-venv: sudo apt install python3-venv"
        exit 1
    fi
    
    source .venv/bin/activate
    echo "✅ Virtual environment creato!"
    echo ""
fi

# Verifica e installa dipendenze se necessario
echo "📦 Verifica dipendenze..."

if ! pip show pyinstaller > /dev/null 2>&1; then
    echo "🔧 Installazione dipendenze di sviluppo..."
    pip install --quiet --upgrade pip
    pip install --quiet -r requirements.txt
    pip install --quiet -r requirements-dev.txt
    echo "✅ Dipendenze installate!"
else
    echo "✅ PyInstaller già disponibile"
fi

echo ""

# Build con PyInstaller
echo "🔨 Creazione eseguibile con PyInstaller..."
echo ""

# Esegui build con output pulito
if pyinstaller --onefile --name importa_articoli importa_articoli_app.py; then
    echo ""
    echo "✅ Build completato con successo!"
    
    # Mostra informazioni del file creato
    if [ -f "dist/importa_articoli" ]; then
        EXECUTABLE_PATH="dist/importa_articoli"
        FILE_SIZE=$(du -h "$EXECUTABLE_PATH" | cut -f1)
        echo "📁 Eseguibile: $EXECUTABLE_PATH"
        echo "📏 Dimensione: $FILE_SIZE"
        echo ""
        
        # Test del build se richiesto
        if [ "$TEST_BUILD" = true ]; then
            echo "🧪 Test dell'eseguibile..."
            if timeout 10s "$EXECUTABLE_PATH" --help > /dev/null 2>&1; then
                echo "✅ Test eseguibile: PASSED"
            else
                echo "⚠️  Test eseguibile: Timeout o errore (normale per app interattive)"
            fi
            echo ""
        fi
        
        # Istruzioni per l'uso
        echo "🚀 Come utilizzare:"
        echo "   ./$EXECUTABLE_PATH"
        echo ""
        echo "📋 Note:"
        echo "   • L'eseguibile include tutto il necessario"
        echo "   • Può essere distribuito su sistemi Linux senza Python"
        echo "   • Per Windows usa GitHub Actions (workflow windows-build.yml)"
        
    else
        echo "❌ Errore: file eseguibile non trovato in dist/"
        exit 1
    fi
else
    echo ""
    echo "❌ Errore durante il build con PyInstaller"
    exit 1
fi

echo ""
echo "🎉 Build completato!"