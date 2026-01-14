#!/usr/bin/env python3
"""
Script interattivo per importare dati da dump MySQL (phpMyAdmin) a database SQLite.
Gestisce importazioni incrementali di file multipli con controllo duplicati.

Uso:
    python import_articoli_to_sqlite.py [file_sql] [database_sqlite]

    Se non viene specificato un file, mostra un menu interattivo.

Esempio:
    python import_articoli_to_sqlite.py                           # Menu interattivo
    python import_articoli_to_sqlite.py t_articoli.sql            # Import diretto
    python import_articoli_to_sqlite.py t_articoli.sql articoli.db
"""

import sqlite3
import sys
import os
import argparse
import logging
import lib.parser as parser


def get_script_dir():
    """Ritorna la directory dello script"""
    return os.path.dirname(os.path.abspath(__file__))


def setup_logging(verbose=False, no_emoji=False):
    """Configura il logging dell'applicazione"""
    level = logging.DEBUG if verbose else logging.INFO
    fmt = "%(message)s"
    logging.basicConfig(level=level, format=fmt)


def get_import_dir():
    """Ritorna il percorso della cartella import"""
    return os.path.join(get_script_dir(), "import")


def clear_screen():
    """Pulisce lo schermo"""
    os.system("clear" if os.name == "posix" else "cls")


def create_database_and_table(db_path):
    """Crea il database SQLite e la tabella se non esistono"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Crea la tabella t_articoli
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS t_articoli (
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

    # Ensure backward-compatible migration: add 'esportato' column if missing
    cursor.execute("PRAGMA table_info(t_articoli)")
    cols = [row[1] for row in cursor.fetchall()]
    if "esportato" not in cols:
        try:
            cursor.execute(
                "ALTER TABLE t_articoli ADD COLUMN esportato INTEGER DEFAULT 0"
            )
        except sqlite3.OperationalError:
            # Some SQLite versions may not allow ALTER; ignore safely
            pass
    conn.commit()
    return conn


# parse_sql_value moved to lib/parser.py (see lib/parser.py)


# extract_tuple_values moved to lib/parser.py (use parser.extract_tuple_values)


class ImportManager:
    """Gestisce l'importazione interattiva dei file SQL"""

    def __init__(self, db_path="articoli.db"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.interactive = True
        self.skip_all_duplicates = False
        self.replace_all_duplicates = False
        self.dry_run = False
        self.use_progress = False

        # Statistiche
        self.imported_count = 0
        self.skipped_count = 0
        self.replaced_count = 0
        self.error_count = 0

    def connect(self):
        """Connette al database"""
        self.conn = create_database_and_table(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def close(self):
        """Chiude la connessione"""
        if self.conn:
            self.conn.commit()
            self.conn.close()

    def get_existing_article(self, article_id):
        """Recupera un articolo esistente per ID"""
        self.cursor.execute(
            "SELECT * FROM t_articoli WHERE id_articolo = ?", (article_id,)
        )
        return self.cursor.fetchone()

    def get_db_stats(self):
        """Ritorna statistiche del database"""
        self.cursor.execute("SELECT COUNT(*) FROM t_articoli")
        count = self.cursor.fetchone()[0]

        if count > 0:
            self.cursor.execute(
                "SELECT MIN(id_articolo), MAX(id_articolo) FROM t_articoli"
            )
            min_id, max_id = self.cursor.fetchone()
            return count, min_id, max_id
        return 0, None, None

    def print_header(self):
        """Stampa l'intestazione"""
        clear_screen()
        print("\n" + "=" * 70)
        print("  📥 IMPORTAZIONE ARTICOLI - MySQL → SQLite")
        print("=" * 70)
        print(f"  Database: {self.db_path}")

        count, min_id, max_id = self.get_db_stats()
        if count > 0:
            print(f"  Record esistenti: {count} (ID: {min_id} - {max_id})")
        else:
            print("  Database vuoto")
        print()

    def show_file_menu(self):
        """Mostra il menu di selezione file"""
        import_dir = get_import_dir()

        # Crea la cartella se non esiste
        if not os.path.exists(import_dir):
            os.makedirs(import_dir)

        # Trova i file SQL
        sql_files = sorted([f for f in os.listdir(import_dir) if f.endswith(".sql")])

        self.print_header()
        print("  📁 FILE DISPONIBILI (cartella import/)\n")
        print("-" * 70)

        if not sql_files:
            print("\n  ⚠️  Nessun file .sql trovato!")
            print("\n  Posiziona i file SQL nella cartella:")
            print(f"     {import_dir}")
            print()
            input("  Premi INVIO per uscire...")
            return None

        for i, f in enumerate(sql_files, 1):
            filepath = os.path.join(import_dir, f)
            size = os.path.getsize(filepath)
            size_str = (
                f"{size / 1024:.1f} KB"
                if size < 1024 * 1024
                else f"{size / (1024*1024):.1f} MB"
            )
            print(f"  {i:2}. {f:<45} ({size_str})")

        print("-" * 70)
        print("\n  [numero] - Seleziona file")
        print("  [a]ll    - Importa tutti i file")
        print("  [q]uit   - Esci")
        print()

        choice = input("  Scelta: ").strip().lower()

        if choice == "q":
            return None
        elif choice == "a":
            return sql_files
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(sql_files):
                return [sql_files[idx]]

        return None

    def handle_duplicate(self, new_values, existing_row):
        """Gestisce un record duplicato"""
        article_id = new_values[0]
        new_title = new_values[3] or "N/D"
        existing_title = existing_row["titolo_articolo"] or "N/D"

        # Se già deciso di saltare tutti o sostituire tutti
        if self.skip_all_duplicates:
            self.skipped_count += 1
            return "skip"
        if self.replace_all_duplicates:
            return "replace"

        # Chiedi all'utente
        print("\n" + "=" * 70)
        print("  ⚠️  ARTICOLO GIÀ PRESENTE!")
        print("=" * 70)
        print(f"\n  ID: {article_id}")
        print("\n  📄 Articolo ESISTENTE:")
        print(f"     Titolo: {existing_title[:60]}")
        print(f"     Data:   {existing_row['data']}")
        print("\n  📄 Articolo NUOVO:")
        print(f"     Titolo: {new_title[:60]}")
        print(f"     Data:   {new_values[1]}")

        print("\n  Cosa vuoi fare?")
        print("    [s]alta     - Mantieni l'esistente")
        print("    [r]impiazza - Sovrascrivi con il nuovo")
        print("    [S]alta TUTTI i duplicati")
        print("    [R]impiazza TUTTI i duplicati")
        print("    [q]uit      - Interrompi importazione")
        print()

        while True:
            choice = input("  Scelta: ").strip()

            if choice == "s":
                self.skipped_count += 1
                return "skip"
            elif choice == "r":
                return "replace"
            elif choice == "S":
                self.skip_all_duplicates = True
                self.skipped_count += 1
                return "skip"
            elif choice == "R":
                self.replace_all_duplicates = True
                return "replace"
            elif choice == "q":
                return "quit"
            else:
                print("  Scelta non valida!")

    def insert_article(self, values):
        """Inserisce o aggiorna un articolo"""
        try:
            if self.dry_run:
                # Simula l'inserimento senza modificare il DB
                logging.debug(f"DRY-RUN: insert {values[0]}")
                return True
            self.cursor.execute(
                """
                INSERT OR REPLACE INTO t_articoli (
                    id_articolo, data, argomento, titolo_articolo, sotto_titolo,
                    TITLE, testo_articolo, nr_attach, titolo_foto, foto_path,
                    link_esterno, contatore_visite, attivo, id_forum,
                    ultimo_accesso, scadenza
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                values,
            )
            return True
        except sqlite3.Error as e:
            logging.error(f"Errore inserimento ID {values[0]}: {e}")
            self.error_count += 1
            return False

    def show_progress(self, current, total, article):
        """Mostra il progresso dell'importazione"""
        title = (article[3] or "N/D")[:50]
        progress = (current / total) * 100 if total > 0 else 0
        bar_width = 40
        filled = int(bar_width * current / total) if total > 0 else 0
        bar = "█" * filled + "░" * (bar_width - filled)

        print(
            f"\r  [{bar}] {progress:5.1f}% | {current}/{total} | {title:<50}",
            end="",
            flush=True,
        )

    def import_file(self, sql_file):
        """Importa i dati da un file SQL"""
        import_dir = get_import_dir()
        filepath = (
            os.path.join(import_dir, sql_file)
            if not os.path.isabs(sql_file)
            else sql_file
        )

        if not os.path.exists(filepath):
            logging.error(f"❌ File non trovato: {filepath}")
            return False

        logging.info(f"📂 Lettura file: {sql_file}")

        # Leggi il file SQL
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Prima passata: conta le tuple
        logging.info("🔍 Analisi contenuto...")
        insert_marker = "INSERT INTO `t_articoli`"
        values_marker = "VALUES"

        # Estrai tutte le tuple
        all_tuples = []
        pos = 0
        while True:
            pos = content.find(insert_marker, pos)
            if pos == -1:
                break

            values_pos = content.find(values_marker, pos)
            if values_pos == -1:
                break

            search_pos = values_pos + len(values_marker)

            while True:
                values, next_pos = parser.extract_tuple_values(content, search_pos)

                if values is None:
                    break

                if len(values) == 16:
                    all_tuples.append(values)

                search_pos = next_pos
                while search_pos < len(content) and content[search_pos] in " \n\r\t":
                    search_pos += 1

                if search_pos >= len(content) or content[search_pos] != ",":
                    break
                search_pos += 1

            pos = search_pos

        total = len(all_tuples)
        logging.info(f"📊 Trovati {total} articoli nel file")

        if total == 0:
            logging.warning("⚠️  Nessun articolo trovato nel file!")
            return False

        # Seconda passata: importa con gestione duplicati
        print("-" * 70)

        if self.use_progress:
            try:
                from tqdm import tqdm
            except Exception:
                logging.warning(
                    "tqdm non disponibile, visualizzazione progressione disabilitata"
                )
                iter_source = enumerate(all_tuples, 1)
            else:
                iter_source = enumerate(
                    tqdm(all_tuples, total=total, unit="articolo", ncols=100), 1
                )

            for i, values in iter_source:
                existing = self.get_existing_article(values[0])

                if existing:
                    if (
                        self.interactive
                        and not self.skip_all_duplicates
                        and not self.replace_all_duplicates
                    ):
                        # In progress mode, avoid inline prompts disrupting tqdm.
                        # Temporarily disable tqdm prints and ask the user.
                        print()  # Nuova riga per il prompt
                        action = self.handle_duplicate(values, existing)

                        if action == "quit":
                            print("\n  🛑 Importazione interrotta dall'utente")
                            return False
                        elif action == "skip":
                            self.skipped_count += 1
                            continue
                        elif action == "replace":
                            if self.insert_article(values):
                                self.replaced_count += 1
                    elif self.skip_all_duplicates:
                        self.skipped_count += 1
                        continue
                    elif self.replace_all_duplicates:
                        if self.insert_article(values):
                            self.replaced_count += 1
                else:
                    if self.insert_article(values):
                        self.imported_count += 1
        else:
            for i, values in enumerate(all_tuples, 1):
                # Verifica duplicato
                existing = self.get_existing_article(values[0])

                if existing:
                    if (
                        self.interactive
                        and not self.skip_all_duplicates
                        and not self.replace_all_duplicates
                    ):
                        # Mostra progresso prima di chiedere
                        print()  # Nuova riga per il prompt
                        action = self.handle_duplicate(values, existing)

                        if action == "quit":
                            print("\n  🛑 Importazione interrotta dall'utente")
                            return False
                        elif action == "skip":
                            self.show_progress(i, total, values)
                            continue
                        elif action == "replace":
                            if self.insert_article(values):
                                self.replaced_count += 1
                    elif self.skip_all_duplicates:
                        self.skipped_count += 1
                        self.show_progress(i, total, values)
                        continue
                    elif self.replace_all_duplicates:
                        if self.insert_article(values):
                            self.replaced_count += 1
                else:
                    # Nuovo articolo
                    if self.insert_article(values):
                        self.imported_count += 1

                self.show_progress(i, total, values)
        print()  # Nuova riga dopo la progress bar
        return True

    def show_summary(self):
        """Mostra il riepilogo dell'importazione"""
        logging.info("\n" + "=" * 70)
        logging.info("✅ IMPORTAZIONE COMPLETATA!")
        logging.info("=" * 70)
        logging.info(f"Nuovi articoli importati:    {self.imported_count}")
        logging.info(f"Articoli aggiornati:         {self.replaced_count}")
        logging.info(f"Articoli saltati:            {self.skipped_count}")
        logging.info(f"Errori:                      {self.error_count}")

        count, min_id, max_id = self.get_db_stats()
        logging.info(f"\n📊 Totale nel database: {count} articoli")
        if count > 0:
            logging.info(f"   Range ID: {min_id} - {max_id}")
        logging.info("=" * 70 + "\n")

    def run_interactive(self):
        """Avvia l'importazione interattiva"""
        self.connect()

        try:
            files = self.show_file_menu()

            if not files:
                return

            for sql_file in files:
                # Reset statistiche per ogni file
                self.imported_count = 0
                self.skipped_count = 0
                self.replaced_count = 0
                self.error_count = 0

                self.print_header()
                print(f"  📥 IMPORTAZIONE: {sql_file}\n")

                self.import_file(sql_file)
                self.conn.commit()

                self.show_summary()

                if len(files) > 1:
                    input("  Premi INVIO per continuare con il prossimo file...")

            print("  ✓ Database SQLite disponibile in:", self.db_path)
            print()

        finally:
            self.close()

    def run_direct(self, sql_file):
        """Importazione diretta (non interattiva per duplicati automatici)"""
        self.connect()
        self.interactive = False
        self.replace_all_duplicates = True  # Default: sostituisci tutti

        try:
            db_exists = os.path.exists(self.db_path)

            if db_exists:
                print(f"Database esistente trovato: {self.db_path}")
                print("I dati verranno aggiunti/aggiornati nel database esistente.\n")
            else:
                print(f"Creazione nuovo database: {self.db_path}\n")

            if self.import_file(sql_file):
                self.conn.commit()
                self.show_summary()
                print(f"  ✓ Database SQLite disponibile in: {self.db_path}")
            else:
                print("  ✗ Importazione fallita!")
                sys.exit(1)

        finally:
            self.close()


def main():
    import_dir = get_import_dir()

    # Crea la cartella import se non esiste
    if not os.path.exists(import_dir):
        os.makedirs(import_dir)

    parser = argparse.ArgumentParser(
        description="Importa file SQL t_articoli in SQLite"
    )
    parser.add_argument(
        "file", nargs="?", help="File SQL da importare (o lascia vuoto per menu)"
    )
    parser.add_argument(
        "--db", "-d", default="articoli.db", help="Nome del database SQLite"
    )
    parser.add_argument(
        "--non-interactive",
        "-n",
        action="store_true",
        help="Modalità non interattiva (sostituisci duplicati)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Simula l'import senza modificare il DB"
    )
    parser.add_argument(
        "--skip-duplicates", action="store_true", help="Skip lista duplicati"
    )
    parser.add_argument(
        "--replace-duplicates", action="store_true", help="Replace lista duplicati"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Modalità verbosa (debug)"
    )
    parser.add_argument("--no-emoji", action="store_true", help="Output senza emoji")
    parser.add_argument(
        "--progress", action="store_true", help="Mostra una barra di progresso con tqdm"
    )
    args = parser.parse_args()

    setup_logging(args.verbose, args.no_emoji)

    # Nessun argomento: modalità interattiva
    if not args.file:
        manager = ImportManager(args.db)
        manager.run_interactive()
        return

    sql_file_arg = args.file
    db_path = args.db

    # Cerca il file SQL nella cartella import
    sql_file = (
        os.path.join(import_dir, sql_file_arg)
        if not os.path.isabs(sql_file_arg)
        else sql_file_arg
    )

    # Se non esiste nella cartella import, prova il percorso originale
    if not os.path.exists(sql_file):
        sql_file = sql_file_arg

    if not os.path.exists(sql_file):
        logging.error(f"❌ File SQL '{sql_file_arg}' non trovato!")
        logging.info(f"\n📁 I file SQL devono essere nella cartella: {import_dir}")

        # Mostra i file disponibili
        if os.path.exists(import_dir):
            sql_files = [f for f in os.listdir(import_dir) if f.endswith(".sql")]
            if sql_files:
                logging.info("\n📄 File SQL disponibili:")
                for f in sorted(sql_files):
                    logging.info(f"   - {f}")
        sys.exit(1)

    manager = ImportManager(db_path)
    manager.dry_run = args.dry_run
    if args.skip_duplicates:
        manager.skip_all_duplicates = True
    if args.replace_duplicates:
        manager.replace_all_duplicates = True
    if args.non_interactive:
        manager.interactive = False
        manager.replace_all_duplicates = True

    manager.run_direct(sql_file)


if __name__ == "__main__":
    main()
