#!/bin/bash
# Script per importare tutti i file SQL dalla cartella import
# 
# Uso:
#   1. Posiziona i file SQL nella cartella 'import/'
#   2. Rendi eseguibile: chmod +x import_all.sh
#   3. Esegui: ./import_all.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Nome del database SQLite di destinazione
DB_NAME="articoli.db"

# Cartella con i file da importare
IMPORT_DIR="$SCRIPT_DIR/import"

# Verifica se la cartella import esiste
if [ ! -d "$IMPORT_DIR" ]; then
    echo "📁 Creazione cartella import..."
    mkdir -p "$IMPORT_DIR"
fi

# Cerca tutti i file SQL nella cartella import
echo "🔍 Ricerca file SQL nella cartella import/..."
FILES=$(ls "$IMPORT_DIR"/*.sql 2>/dev/null | sort)

if [ -z "$FILES" ]; then
    echo "❌ Nessun file SQL trovato nella cartella 'import/'"
    echo ""
    echo "Posiziona i file SQL nella cartella import/ con nomi come:"
    echo "  - t_articoli.sql"
    echo "  - t_articoli_001.sql, t_articoli_002.sql, ecc."
    exit 1
fi

# Conta i file
FILE_COUNT=$(echo "$FILES" | wc -l)
echo "✅ Trovati $FILE_COUNT file SQL"
echo ""

# Chiedi conferma
read -p "Vuoi importare tutti i file nel database '$DB_NAME'? (s/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo "Operazione annullata."
    exit 0
fi

echo ""
echo "📊 Inizio importazione..."
echo "========================================"

# Contatori
CURRENT=0
START_TIME=$(date +%s)

# Importa ogni file
for FILE in $FILES; do
    CURRENT=$((CURRENT + 1))
    BASENAME=$(basename "$FILE")
    echo ""
    echo "[$CURRENT/$FILE_COUNT] Importazione di: $BASENAME"
    echo "----------------------------------------"
    
    python3 import_articoli_to_sqlite.py "$BASENAME" "$DB_NAME"
    
    if [ $? -ne 0 ]; then
        echo "❌ Errore durante l'importazione di $FILE"
        read -p "Vuoi continuare con i file rimanenti? (s/n) " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Ss]$ ]]; then
            echo "Importazione interrotta."
            exit 1
        fi
    fi
done

END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))

echo ""
echo "========================================"
echo "✅ Importazione completata!"
echo "========================================"
echo "File processati: $FILE_COUNT"
echo "Tempo impiegato: ${ELAPSED}s"
echo ""

# Mostra statistiche finali
echo "📈 Statistiche finali del database:"
python3 << EOF
import sqlite3

conn = sqlite3.connect('$DB_NAME')
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM t_articoli")
total = cursor.fetchone()[0]

cursor.execute("SELECT MIN(id_articolo), MAX(id_articolo) FROM t_articoli")
min_id, max_id = cursor.fetchone()

cursor.execute("SELECT COUNT(DISTINCT argomento) FROM t_articoli")
argomenti = cursor.fetchone()[0]

print(f"  Totale articoli: {total}")
print(f"  Range ID: {min_id} - {max_id}")
print(f"  Argomenti univoci: {argomenti}")

# Top 5 argomenti
cursor.execute("""
    SELECT argomento, COUNT(*) as cnt 
    FROM t_articoli 
    GROUP BY argomento 
    ORDER BY cnt DESC 
    LIMIT 5
""")
print(f"\n  Top 5 argomenti:")
for arg, cnt in cursor.fetchall():
    print(f"    - {arg}: {cnt} articoli")

conn.close()
EOF

echo ""
echo "✅ Database '$DB_NAME' pronto per l'uso!"
