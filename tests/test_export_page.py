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

    for i in range(1, 6):
        cur.execute(
            """
            INSERT INTO t_articoli (
                id_articolo, data, argomento, titolo_articolo, testo_articolo
            ) VALUES (?, date('now'), ?, ?, ?)
            """,
            (i, "arg", f"title {i}", f"body {i}"),
        )
    conn.commit()
    conn.close()


def test_export_page_fetches_full_articles(tmp_path):
    db = tmp_path / "test_export.db"
    create_test_db(db)

    explorer = ArticoliExplorer(str(db))
    assert explorer.connect()

    # Simulate the summary rows returned by get_articles_page
    explorer.cursor.execute(
        (
            "SELECT id_articolo, data, argomento, titolo_articolo, "
            "sotto_titolo, esportato "
            "FROM t_articoli "
            "ORDER BY data DESC LIMIT ?"
        ),
        (5,),
    )
    rows = explorer.cursor.fetchall()

    # Export the page: rows lack 'testo_articolo', exporter must fetch full rows
    exported = explorer.export_articles(rows, mark_exported=True, limit=5)
    assert exported == 5

    # Verify DB exported flags
    explorer.cursor.execute(
        "SELECT COUNT(*) FROM t_articoli " "WHERE esportato = 1",
    )
    count = explorer.cursor.fetchone()[0]
    explorer.close()
    assert count == 5
