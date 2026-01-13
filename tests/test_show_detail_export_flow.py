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
        ) VALUES (
            1, date('now'), 'arg', 'Some title', 'Some body'
        )
        """
    )
    conn.commit()
    conn.close()


def test_show_detail_export_flow(tmp_path, monkeypatch, capsys):
    db = tmp_path / "test_export.db"
    create_test_db(db)

    explorer = ArticoliExplorer(str(db))
    assert explorer.connect()

    article = explorer.get_article_by_id(1)

    # Simulate user pressing 'e' then Enter to return
    inputs = iter(
        [
            "e",
            "",
        ]
    )  # 'e' to export, then '' to press Enter at prompt

    def fake_input(prompt=""):
        return next(inputs)

    monkeypatch.setattr("builtins.input", fake_input)

    explorer.show_article_detail(article)

    # After returning, the DB record should be marked as exported
    explorer.cursor.execute("SELECT esportato FROM t_articoli WHERE id_articolo = 1")
    exported_flag = explorer.cursor.fetchone()[0]
    explorer.close()

    assert exported_flag == 1
