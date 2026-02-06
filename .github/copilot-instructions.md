# Copilot Instructions - Import Articoli Ficiesse

## Architecture Overview

Python tool for migrating MySQL dumps (phpMyAdmin exports) to SQLite with DOCX export capabilities.

| Component | Description |
|-----------|-------------|
| `import_articoli_to_sqlite.py` | Import: SQL parser + SQLite writer with upsert |
| `esplora_articoli.py` | Explorer + DOCX exporter with `esportato` tracking |
| `lib/parser.py` | Reusable SQL tuple parser (`extract_tuple_values`, `parse_sql_value`) |
| `importa_articoli_app.py` | Unified launcher with interactive menu |

**Data Flow**: `.sql` files → `lib/parser.py` extracts tuples → SQLite via `INSERT OR REPLACE` on `id_articolo` PK

## Critical Pattern: Fixed 16+1 Column Schema

The table has **16 original columns + 1 tracking column** (`esportato`). Parser rejects rows with != 16 values.

**When modifying schema, update ALL of these:**
1. `create_database_and_table()` in [import_articoli_to_sqlite.py](../import_articoli_to_sqlite.py#L49)
2. Validation check: `if len(values) != 16`
3. INSERT statement must **explicitly list 16 columns** (excludes `esportato`)
4. Migration logic for existing DBs (see `ALTER TABLE` pattern for `esportato`)
5. Test fixtures in `tests/`

## Parser Specifics (lib/parser.py)

Handles MySQL escapes that regex can't parse reliably:
- Escaped quotes: `\'` → `'`, `\"` → `"`, `\\` → `\`
- HTML content with quoted attributes inside SQL strings
- Nested parentheses and commas inside strings (uses `paren_level` counter)

## Essential Commands

```bash
# Import with progress bar
python import_articoli_to_sqlite.py import/t_articoli.sql --db articoli.db --progress

# Dry-run validation
python import_articoli_to_sqlite.py import/t_articoli.sql --dry-run --verbose

# Export only new articles (marks esportato=1 after export)
python esplora_articoli.py articoli.db --export-all --export-only-new --export-limit 50

# Run tests
pytest -v

# Quality checks (CI enforced)
black --check . && flake8 && mypy --config-file mypy.ini

# Build Windows executable
pyinstaller --onefile --name importa_articoli importa_articoli_app.py
```

## Conventions

- **SQL files**: Place in `import/` folder, pattern `t_articoli_*.sql` for batch recognition
- **Output DB**: Default `articoli.db` in project root
- **Exports**: Auto-created `./exports/` directory
- **Cross-platform**: Maintain both `.sh` (Linux) and `.bat` (Windows) variants for scripts
- **Code style**: Black (line-length 88, Python 3.12), flake8, mypy (see `pyproject.toml`, `mypy.ini`)
- **Testing**: pytest with `tmp_path` for temp DBs, `monkeypatch` for interactive input mocking

## Key Constraints

- **Export limit**: `MAX_EXPORT_LIMIT = 50` per call (memory protection)
- **Single commit**: Import commits only at end of file (not per-row) for performance
- **Dual mode**: Scripts support both interactive (default) and non-interactive (`--non-interactive`, `--export-all`)
