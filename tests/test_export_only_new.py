import sqlite3
import subprocess
import sys
from pathlib import Path


def create_test_db(path):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE t_articoli (
            id_articolo INTEGER PRIMARY KEY,
            data TEXT,
            argomento TEXT,
            titolo_articolo TEXT,
            sotto_titolo TEXT,
            TITLE TEXT,
            testo_articolo TEXT,
            nr_attach INTEGER,
            titolo_foto TEXT,
            foto_path TEXT,
            link_esterno TEXT,
            contatore_visite INTEGER,
            attivo INTEGER,
            id_forum INTEGER,
            ultimo_accesso TEXT,
            scadenza TEXT,
            esportato INTEGER DEFAULT 0
        )
    """
    )

    # Insert 3 articles, mark the first as already exported
    for i in range(1, 4):
        exported = 1 if i == 1 else 0
        cur.execute(
            (
                "INSERT INTO t_articoli (id_articolo, data, argomento, "
                "titolo_articolo, testo_articolo, esportato) "
                "VALUES (?, date('now'), ?, ?, ?, ?)"
            ),
            (i, "arg", f"title {i}", f"body {i}", exported),
        )
    conn.commit()
    conn.close()


def test_export_only_new(tmp_path):
    db = tmp_path / "test_export.db"
    create_test_db(db)

    # Clean export folder
    out_dir = Path("export")
    if out_dir.exists():
        for f in out_dir.glob("articolo_*.docx"):
            f.unlink()

    # Run esplora in non-interactive export-only-new mode
    cmd = [
        sys.executable,
        "esplora_articoli.py",
        str(db),
        "--export-all",
        "--export-only-new",
        "--export-limit",
        "10",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)

    files = list(out_dir.glob("articolo_*.docx"))

    # The DB had 3 articles, 1 already exported; expect 2 new exports
    assert res.returncode == 0
    assert len(files) >= 2

    # Verify DB exported flags: should be at least 3 exported now
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM t_articoli WHERE esportato = 1")
    count = cur.fetchone()[0]
    conn.close()

    assert count >= 3
