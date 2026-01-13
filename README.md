# Script di Importazione MySQL → SQLite

## Descrizione

Questo script Python importa dati da file SQL esportati da phpMyAdmin (MySQL) in un database SQLite. 

**Caratteristiche principali:**
- ✅ Crea automaticamente il database SQLite se non esiste
- ✅ Gestisce importazioni incrementali (più file successivi)
- ✅ Aggiorna automaticamente i record duplicati (basandosi su `id_articolo`)
- ✅ Gestisce correttamente stringhe con caratteri speciali, HTML, escape, ecc.
- ✅ Mostra statistiche dettagliate al termine dell'importazione

## Requisiti

- Python 3.8 o superiore (consigliato)
- Modulo `sqlite3` (incluso in Python standard)

## Installazione

Si consiglia di usare un virtualenv:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Per le funzionalità opzionali (export DOCX, parsing avanzato, progress bar e test) installa le dipendenze:

```bash
pip install -r requirements.txt
```

Le dipendenze opzionali includono `python-docx`, `htmldocx`, `beautifulsoup4`, `tqdm` e `pytest`.

Nota: puoi abilitare la barra di progresso nell'import con `--progress`.

## Struttura della Tabella

La tabella `t_articoli` ha 16 colonne:
1. `id_articolo` (INTEGER PRIMARY KEY)
2. `data` (TEXT)
3. `argomento` (TEXT)
4. `titolo_articolo` (TEXT)
5. `sotto_titolo` (TEXT)
6. `TITLE` (TEXT)
7. `testo_articolo` (TEXT)
8. `nr_attach` (INTEGER)
9. `titolo_foto` (TEXT)
10. `foto_path` (TEXT)
11. `link_esterno` (TEXT)
12. `contatore_visite` (INTEGER)
13. `attivo` (INTEGER)
14. `id_forum` (INTEGER)
15. `ultimo_accesso` (TEXT)
16. `scadenza` (TEXT)

## Uso

### Sintassi di base

```bash
# Menu interattivo
python import_articoli_to_sqlite.py

# Import diretto: file (nella cartella import/) e DB
python import_articoli_to_sqlite.py <file_sql> --db nome_database.db

# Opzioni utili: --dry-run, --non-interactive, --verbose
python import_articoli_to_sqlite.py t_articoli_1.sql --db articoli.db --dry-run --verbose
```

### Parametri

- `<file_sql>`: **Obbligatorio** - Percorso del file SQL da importare
- `[nome_database.db]`: **Opzionale** - Nome del database SQLite (default: `articoli.db`)

## Esplorazione ed export DOCX

Lo script `esplora_articoli.py` offre un'interfaccia terminale per navigare e esportare articoli in DOCX.

Flags principali:

- `--page-size N` : imposta il numero di articoli per pagina nell'esploratore
- `--export-all` : esegue l'export non interattivo dei risultati (uno file DOCX per articolo)
- `--export-only-new` : quando usato con `--export-all`, esporta solo articoli non ancora marcati come "esportato" (colonna `esportato`)
- `--export-limit N` : numero massimo di articoli da esportare in una singola invocazione (default: 50; server-side enforced)

Comportamenti importanti:
- Ogni articolo esportato viene marcato con `esportato = 1` per evitare duplicati futuri se `--export-only-new` è usato.
- Il limite massimo di export per chiamata è **50** (per evitare blocchi o uso eccessivo di memoria). Se si richiede più di 50, verranno esportati solo i primi 50.

Esempio non-interattivo (esporta solo articoli non ancora esportati):

```bash
python esplora_articoli.py articoli.db --export-all --export-only-new --export-limit 20
```

Nota: le funzionalità di export richiedono `python-docx` (obbligatorio) e opzionalmente `htmldocx` e `beautifulsoup4` per convertire HTML ed avere anteprime migliori.

## Esempi

### Prima importazione (prime 50 righe)

```bash
python import_articoli_to_sqlite.py t_articoli_1.sql articoli.db
```

Output:
```
Creazione nuovo database: articoli.db

Lettura file: t_articoli_1.sql
  Importate 50 righe...
============================================================
Importazione completata!
============================================================
Nuove righe importate:      50
Righe già presenti:         0
Errori:                     0
Totale record nel database: 50
============================================================

✓ Database SQLite disponibile in: articoli.db
```

### Importazioni successive (righe 51-110, 111-170, ecc.)

```bash
# Importa righe 51-110
python import_articoli_to_sqlite.py t_articoli_2.sql articoli.db

# Importa righe 111-170
python import_articoli_to_sqlite.py t_articoli_3.sql articoli.db

# E così via...
```

Output tipico:
```
Database esistente trovato: articoli.db
I dati verranno aggiunti/aggiornati nel database esistente.

Lettura file: t_articoli_2.sql
  Importate 60 righe...
============================================================
Importazione completata!
============================================================
Nuove righe importate:      60
Righe già presenti:         0
Errori:                     0
Totale record nel database: 110
============================================================
```

## Gestione Duplicati

Se importi un file che contiene righe già presenti (stesso `id_articolo`), lo script:
- **Sostituisce** il record esistente con i nuovi dati
- Conta il record come "già presente" nelle statistiche

Esempio:
```bash
python import_articoli_to_sqlite.py t_articoli_aggiornato.sql articoli.db
```

Output:
```
============================================================
Nuove righe importate:      45
Righe già presenti:         5    ← 5 record aggiornati
Errori:                     0
Totale record nel database: 7045
============================================================
```

## Interrogare il Database

Dopo l'importazione, puoi interrogare il database con:

### Con sqlite3 (command line)

```bash
sqlite3 articoli.db
```

### Usare l'interfaccia di esplorazione

```bash
# Avvia l'esploratore (opzioni: --page-size, --verbose)
python esplora_articoli.py articoli.db --page-size 20
```

```bash
sqlite3 articoli.db
```

Poi esegui query SQL:
```sql
SELECT COUNT(*) FROM t_articoli;
SELECT * FROM t_articoli WHERE id_articolo = 100;
SELECT * FROM t_articoli ORDER BY data DESC LIMIT 10;
```

### Con Python

```python
import sqlite3

conn = sqlite3.connect('articoli.db')
cursor = conn.cursor()

# Conta tutti gli articoli
cursor.execute("SELECT COUNT(*) FROM t_articoli")
print(f"Totale articoli: {cursor.fetchone()[0]}")

# Cerca per titolo
cursor.execute("SELECT * FROM t_articoli WHERE titolo_articolo LIKE ?", ('%COCER%',))
for row in cursor.fetchall():
    print(row)

conn.close()
```

## Workflow Completo

Per importare tutte le 7000+ righe:

1. **Esporta da phpMyAdmin in blocchi di 50-100 righe:**
   - `t_articoli_001.sql` (righe 1-50)
   - `t_articoli_002.sql` (righe 51-100)
   - `t_articoli_003.sql` (righe 101-150)
   - ... ecc.

2. **Importa tutti i file sequenzialmente:**
   ```bash
   python import_articoli_to_sqlite.py t_articoli_001.sql articoli.db
   python import_articoli_to_sqlite.py t_articoli_002.sql articoli.db
   python import_articoli_to_sqlite.py t_articoli_003.sql articoli.db
   # ...continua per tutti i file
   ```

3. **Verifica il risultato finale:**
   ```bash
   python3 << 'EOF'
   import sqlite3
   conn = sqlite3.connect('articoli.db')
   cursor = conn.cursor()
   cursor.execute("SELECT COUNT(*) FROM t_articoli")
   print(f"Totale record importati: {cursor.fetchone()[0]}")
   conn.close()
   EOF
   ```

## Note Importanti

- ⚠️ **Backup:** Lo script usa `INSERT OR REPLACE`, quindi record esistenti vengono sovrascritti
- ⚠️ **Encoding:** I file SQL devono essere in UTF-8
- ⚠️ **Formato:** Lo script è ottimizzato per file esportati da phpMyAdmin
- ⚠️ **Performance:** L'importazione è veloce (~10 record/secondo)

## Eseguire i test

I test unitari si trovano nella cartella `tests/` (usano `pytest`). Per eseguirli:

```bash
pip install -r requirements.txt
pytest -q
```

## Risoluzione Problemi

### Errore "File non trovato"
```
Errore: File 't_articoli.sql' non trovato!
```
**Soluzione:** Verifica il percorso del file SQL

### Errore "riga con X valori invece di 16"
```
Attenzione: riga con 15 valori invece di 16, saltata
```
**Soluzione:** Il file SQL potrebbe essere corrotto o non nel formato atteso

### Database non si crea
**Soluzione:** Verifica di avere i permessi di scrittura nella directory

## Licenza

Script fornito "as-is" per uso personale.
