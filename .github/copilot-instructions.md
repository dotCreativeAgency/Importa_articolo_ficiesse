# Istruzioni per Copilot - Import Articoli Ficiesse

## Panoramica del Progetto

Sistema Python per migrare dati da dump MySQL (phpMyAdmin) a SQLite con capacità di esplorazione ed export. Tre componenti principali:
1. **Import**: Parser SQL custom per importazioni incrementali con upsert automatico
2. **Explorer**: Interfaccia terminale per navigare articoli con paginazione e ricerca
3. **Exporter**: Generazione DOCX con conversione HTML e tracking export (`esportato` flag)

## Architettura

```
importa_articoli_app.py       # Launcher unificato con menu principale
import_articoli_to_sqlite.py  # Import: parser SQL + SQLite writer
esplora_articoli.py           # Explorer/Exporter con CLI/interfaccia interattiva
lib/parser.py                 # Parser SQL riutilizzabile (extract_tuple_values, parse_sql_value)
import/                       # Cartella per file .sql da importare
tests/                        # Test unitari (pytest) e integration tests
scripts/build_windows.sh      # Build PyInstaller per eseguibile Windows
```

### Data Flow — Import
1. **Input**: File `.sql` con `INSERT INTO t_articoli VALUES (...)` esportati da phpMyAdmin
2. **Parsing**: `lib/parser.py` estrae tuple gestendo escape (`\'`, `\"`, `\\`), HTML embedded, `NULL`
3. **Storage**: SQLite con `INSERT OR REPLACE` (upsert su `id_articolo` PK)
4. **Tracking**: Colonna `esportato` (default 0) aggiunta automaticamente se mancante

### Data Flow — Export
1. **Query**: Fetch articoli con filtri (argomento/ricerca) e paginazione
2. **Conversione**: HTML → DOCX via `htmldocx` + `BeautifulSoup4` per contenuto `testo_articolo`
3. **Output**: Un file DOCX per articolo in `./exports/`
4. **Marking**: `UPDATE t_articoli SET esportato=1` per evitare duplicati con `--export-only-new`

## Pattern Critici

### Schema Fisso 16+1 Colonne
La tabella ha **16 colonne originali + 1 aggiunta** (`esportato`). Il parser rifiuta righe con numero diverso da 16:
```python
# In import_articoli_to_sqlite.py
if len(values) != 16:
    print(f"Attenzione: riga con {len(values)} valori invece di 16, saltata")
```
**Attenzione**: Quando modifichi lo schema, aggiorna:
- `create_database_and_table()` (definizione SQL)
- Controllo `len(values) != 16`
- `insert_article()` — L'INSERT **deve elencare esplicitamente le colonne** per escludere `esportato`:
  ```python
  INSERT OR REPLACE INTO t_articoli (
      id_articolo, data, argomento, ...16 colonne...
  ) VALUES (?, ?, ?, ...)
  ```
- Test in `tests/test_import_progress.py`

### Parser SQL Custom (lib/parser.py)
Gestisce complessità MySQL non parsabili con regex semplici:
- Stringhe con apici singoli e escape (`'it\'s ok'` → `it's ok`)
- HTML embedded con attributi quotati
- Parentesi e virgole dentro stringhe
- Livelli di nesting con `paren_level` counter

```python
# Escape handling in parse_sql_value()
value = value.replace("\\'", "'")
value = value.replace('\\"', '"')
value = value.replace('\\\\', '\\')
```

### Export Safeguards
```python
# In esplora_articoli.py - MAX_EXPORT_LIMIT costante
MAX_EXPORT_LIMIT = 50  # Server-side enforced per evitare blocchi
```
Il limite di 50 export per chiamata previene uso eccessivo di memoria e blocchi. Per export massivi, usa batch con `--export-only-new`.

### Interactive vs Non-Interactive Mode
Gli script supportano entrambi i modi:
- **Interactive**: Menu con prompt utente (default se nessun argomento)
- **Non-interactive**: Flags CLI per automazione (`--non-interactive`, `--export-all`, `--dry-run`)

## Comandi Essenziali

### Import Workflows
```bash
# Import interattivo (menu con selezione file)
python import_articoli_to_sqlite.py

# Import diretto con progress bar
python import_articoli_to_sqlite.py import/t_articoli_001.sql --db articoli.db --progress

# Dry-run per validazione senza scrivere DB
python import_articoli_to_sqlite.py import/t_articoli.sql --dry-run --verbose

# Batch import tutti i file nella cartella import/
./import_all.sh  # Linux
import_all.bat   # Windows
```

### Export Workflows
```bash
# Explorer interattivo con paginazione
python esplora_articoli.py articoli.db --page-size 20

# Export non-interattivo (solo articoli non esportati)
python esplora_articoli.py articoli.db --export-all --export-only-new --export-limit 50

# Export forzato di tutti (ignora flag esportato)
python esplora_articoli.py articoli.db --export-all --export-limit 50
```

### Testing & Quality
```bash
# Test unitari e integration
pytest -v

# Linting e formatting (CI workflow compliant)
black --check .
flake8
mypy --config-file mypy.ini

# Build eseguibile Windows (genera dist/importa_articoli.exe)
pip install -r requirements-dev.txt
pyinstaller --onefile --name importa_articoli importa_articoli_app.py
```

### Database Operations
```bash
# Verifica conteggio e stato export
sqlite3 articoli.db "SELECT COUNT(*), SUM(esportato) FROM t_articoli"

# Reset flag export per re-export
sqlite3 articoli.db "UPDATE t_articoli SET esportato=0"

# Query argomenti disponibili
sqlite3 articoli.db "SELECT DISTINCT argomento FROM t_articoli ORDER BY argomento"
```

## Convenzioni e Best Practices

### File Naming & Structure
- **SQL imports**: Pattern `t_articoli_*.sql` per riconoscimento batch (posiziona in `import/`)
- **Output DB**: Default `articoli.db` (radice progetto)
- **Exports**: Directory `./exports/` generata automaticamente
- **Test fixtures**: `tmp_path` pytest per DB temporanei (vedi `tests/test_export_*.py`)

### Code Style (CI Enforced)
- **Formatter**: Black (line-length 88, target Python 3.12)
- **Linter**: flake8 (config in `.flake8` se presente)
- **Type Hints**: mypy configurato (`mypy.ini`) - coverage parziale ma in crescita
- **Test Coverage**: pytest per unit + integration tests

### Dependency Management
- **Required**: Solo `sqlite3` (stdlib) per import base
- **Optional**: `python-docx`, `htmldocx`, `bs4`, `tqdm` (vedi `requirements.txt`)
- **Dev**: `black`, `flake8`, `mypy`, `pytest`, `pyinstaller` (vedi `requirements-dev.txt`)

### Cross-Platform Support
- Shell scripts duplicati: `.sh` (Linux) e `.bat` (Windows)
- Launcher unificato: `importa_articoli_app.py` con logic condivisa
- PyInstaller per distribuzione eseguibile Windows (GitHub Actions workflow `windows-build.yml`)

## Test Strategy

### Unit Tests (lib/parser.py)
- `test_parser.py`: Parse SQL values, escape handling, tuple extraction
- Focus: Edge cases con apici, parentesi, HTML, NULL values

### Integration Tests (end-to-end)
- `test_export_*.py`: Export multiplo, flag `esportato`, page fetching
- `test_import_progress.py`: Import con progress bar, dry-run mode
- `test_importa_articoli_app.py`: Menu dispatch e safe module execution

### Testing Patterns
```python
# Usa tmp_path per DB temporanei
def test_export_all_creates_files(tmp_path):
    db = tmp_path / "test.db"
    conn = sqlite3.connect(db)
    # ... setup e assertions

# Mock input per test interattivi
def test_menu_dispatch(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _: "1")
```

## Modifiche Comuni

### Aggiungere Colonna a t_articoli
1. Modifica `create_database_and_table()` → Aggiungi colonna in CREATE TABLE
2. Aggiungi migration per DB esistenti (vedi pattern `esportato` con `ALTER TABLE`)
3. Aggiorna parsing se colonna è in tuple SQL (cambia controllo `!= 16` se necessario)
4. Aggiorna test fixtures in `tests/`

### Estendere Export Format
- Implementa in `esplora_articoli.py` → Metodo `export_article_to_docx()`
- Vedi pattern conversione HTML: `HtmlToDocx`, `BeautifulSoup` per cleanup
- Testa con `tests/test_export_single_marks.py` come template

### Nuovi Batch Scripts
- Duplica `import_all.sh` → Usa pattern `ls "$IMPORT_DIR"/*.sql | sort`
- Mantieni logica conferma utente e statistiche finali
- Sincronizza con `.bat` per Windows (vedi `import_all.bat`)

## Performance Notes

- **Single commit**: Import esegue commit solo a fine file (non per-row) per performance
- **Batch size**: Export limitato a 50 per chiamata per evitare OOM su grandi dataset
- **Indexing**: `id_articolo` è PRIMARY KEY → lookup veloci per upsert
- **Progress**: Usa `tqdm` per visibility su import lunghi (`--progress` flag)

## Debugging Tips

```bash
# Verbose logging per troubleshooting parser
python import_articoli_to_sqlite.py file.sql --verbose

# Dry-run senza modificare DB
python import_articoli_to_sqlite.py file.sql --dry-run

# Test singolo con output dettagliato
pytest -vv tests/test_parser.py::test_extract_tuple_with_parentheses_in_string

# Verifica schema DB
sqlite3 articoli.db ".schema t_articoli"
```
