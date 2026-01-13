from esplora_articoli import ArticoliExplorer
import sqlite3


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
        ) VALUES (
            1, date('now'), 'arg',
            'This is a very long title that should be shown in full on the second line',
            'body'
        )
        """
    )
    conn.commit()
    conn.close()


def test_print_shows_full_title(tmp_path, capsys):
    db = tmp_path / "test_export.db"
    create_test_db(db)

    explorer = ArticoliExplorer(str(db))
    assert explorer.connect()

    explorer.cursor.execute(
        (
            "SELECT id_articolo, data, argomento, titolo_articolo, "
            "sotto_titolo, esportato FROM t_articoli"
        )
    )
    rows = explorer.cursor.fetchall()

    explorer.print_articles_list(rows)
    captured = capsys.readouterr()
    # Ensure the long title appears in output
    assert "This is a very long title that should be shown in full" in captured.out
