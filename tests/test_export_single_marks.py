import sqlite3

from esplora_articoli import ArticoliExplorer


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

    cur.execute(
        """
        INSERT INTO t_articoli (
            id_articolo, data, argomento, titolo_articolo, testo_articolo
        ) VALUES (?, date('now'), ?, ?, ?)
        """,
        (1, "arg", "single title", "single body"),
    )
    conn.commit()
    conn.close()


def test_export_single_marks_exported(tmp_path):
    db = tmp_path / "test_export.db"
    create_test_db(db)

    explorer = ArticoliExplorer(str(db))
    assert explorer.connect()

    explorer.cursor.execute("SELECT * FROM t_articoli LIMIT 1")
    article = explorer.cursor.fetchone()

    # Export single article and request marking
    out = explorer.export_article(article, interactive=False, mark_exported=True)
    assert out is not None

    explorer.cursor.execute(
        "SELECT esportato FROM t_articoli " "WHERE id_articolo = 1",
    )
    exported_flag = explorer.cursor.fetchone()[0]
    explorer.close()

    assert exported_flag == 1
