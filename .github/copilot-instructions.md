# Istruzioni per Copilot - Import Articoli Ficiesse

## Panoramica del Progetto

Strumento Python per migrare dati da dump MySQL (phpMyAdmin) a SQLite. Gestisce importazioni incrementali di file multipli con una tabella a 16 colonne (`t_articoli`).

## Architettura

```
import_articoli_to_sqlite.py  # Script principale - parser SQL + import SQLite
import_all.sh                 # Batch import Linux (pattern t_articoli_*.sql)
import_all.bat                # Batch import Windows
articoli.db                   # Database SQLite di output (generato)
```

### Flusso Dati
1. **Input**: File `.sql` esportati da phpMyAdmin con `INSERT INTO t_articoli VALUES (...)`
2. **Parsing**: Estrazione tuple SQL con gestione escape (`\'`, `\"`, `\\`)
3. **Output**: Database SQLite con `INSERT OR REPLACE` (upsert su `id_articolo`)

## Pattern Critici

### Parser SQL Custom
Il parser in `extract_tuple_values()` gestisce casi complessi:
- Stringhe con apici singoli e caratteri escapati
- Contenuto HTML embedded nei valori
- Valori `NULL` convertiti a `None`
- Parentesi annidate nei valori

```python
# Esempio di gestione escape in parse_sql_value()
value = value.replace("\\'", "'")
value = value.replace('\\"', '"')
value = value.replace('\\\\', '\\')
```

### Schema Tabella Fisso
La tabella ha esattamente **16 colonne** - il parser rifiuta righe con numero diverso:
```python
if len(values) != 16:
    print(f"Attenzione: riga con {len(values)} valori invece di 16, saltata")
```

## Comandi di Sviluppo

```bash
# Import singolo file
python3 import_articoli_to_sqlite.py t_articoli_001.sql articoli.db

# Import batch (Linux) - cerca t_articoli_*.sql nella directory corrente
./import_all.sh

# Verifica database
sqlite3 articoli.db "SELECT COUNT(*) FROM t_articoli"
```

## Convenzioni

- **Encoding**: File SQL in UTF-8
- **Naming file**: Pattern `t_articoli_XXX.sql` per batch import
- **Output**: Database default `articoli.db` se non specificato
- **Statistiche**: Lo script mostra sempre conteggio importate/duplicate/errori

## Punti di Attenzione per Modifiche

1. **Modifiche allo schema**: Aggiornare sia `create_database_and_table()` che il controllo `len(values) != 16`
2. **Nuovi escape SQL**: Estendere `parse_sql_value()` per nuovi caratteri
3. **Performance**: Commit singolo a fine import, non per ogni riga
4. **Cross-platform**: Mantenere sincronizzati `import_all.sh` e `import_all.bat`
