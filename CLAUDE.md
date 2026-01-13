# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python tool for migrating data from MySQL dumps (phpMyAdmin exports) to SQLite. Handles incremental imports of multiple SQL files with a fixed 16-column table schema (`t_articoli`).

## Commands

```bash
# Import a single SQL file
python3 import_articoli_to_sqlite.py t_articoli_001.sql articoli.db

# Batch import all SQL files (Linux) - expects t_articoli_*.sql pattern
./import_all.sh

# Batch import (Windows)
import_all.bat

# Verify database contents
sqlite3 articoli.db "SELECT COUNT(*) FROM t_articoli"
```

## Architecture

### Data Flow
1. **Input**: `.sql` files exported from phpMyAdmin with `INSERT INTO t_articoli VALUES (...)`
2. **Parsing**: Custom SQL parser extracts tuple values, handling escapes (`\'`, `\"`, `\\`)
3. **Output**: SQLite database using `INSERT OR REPLACE` (upsert on `id_articolo`)

### Key Components

**`import_articoli_to_sqlite.py`** - Main script with three core functions:
- `create_database_and_table()` - Creates SQLite schema if not exists
- `extract_tuple_values()` - Custom parser for SQL INSERT tuples (handles quoted strings, escapes, nested parentheses, HTML content)
- `parse_sql_value()` - Converts SQL values to Python types (NULL→None, numbers, strings with unescaping)

**`import_all.sh` / `import_all.bat`** - Batch processors that find `t_articoli_*.sql` files and import them sequentially, showing progress and final statistics.

## Critical Implementation Details

### Fixed 16-Column Schema
The parser strictly enforces 16 columns per row - rows with different counts are skipped:
```python
if len(values) != 16:
    print(f"Attenzione: riga con {len(values)} valori invece di 16, saltata")
```

When modifying the schema, update both `create_database_and_table()` and this validation check.

### SQL Escape Handling
The parser handles MySQL escapes that must be preserved:
```python
value = value.replace("\\'", "'")
value = value.replace('\\"', '"')
value = value.replace('\\\\', '\\')
```

### Performance
Single commit at end of import (not per-row) - important for large imports.

## Conventions

- **Encoding**: SQL files must be UTF-8
- **File naming**: Pattern `t_articoli_XXX.sql` for batch import recognition
- **Default output**: `articoli.db` if database name not specified
