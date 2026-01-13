#!/usr/bin/env python3
"""Launcher unificato: permette di scegliere tra importare nuovi articoli o
esplorare/esportare.

Il launcher esegue i `main()` dei moduli esistenti in-process in modo sicuro
(cattura SystemExit) così da tornare al menu principale dopo che l'operazione è
terminata.
"""
from __future__ import annotations

import importlib
import logging
import sys
from typing import Sequence

logging.basicConfig(level=logging.INFO)


def safe_run_module_main(module_name: str, argv: Sequence[str] | None = None) -> None:
    """Importa il modulo e chiama la sua funzione `main()` in modo sicuro.

    Se viene passato `argv`, viene temporaneamente sovrascritto `sys.argv`.
    Eventuali SystemExit sollevati dai moduli vengono catturati e ignorati.
    """
    module = importlib.import_module(module_name)
    old_argv = sys.argv
    if argv is not None:
        sys.argv = [module_name] + list(argv)
    try:
        if hasattr(module, "main"):
            module.main()
        else:
            # fallback: esegui il modulo come script
            import runpy

            runpy.run_module(module_name, run_name="__main__")
    except SystemExit:
        # Lanciare SystemExit nei moduli non deve terminare questo launcher
        logging.debug("Modulo %s terminato con SystemExit", module_name)
    finally:
        sys.argv = old_argv


def prompt_menu() -> None:
    while True:
        print("\n=== Importa & Esporta Articoli — Menu Principale ===")
        print("1) Importa nuovi articoli (da file .sql)")
        print("2) Esplora / Esporta articoli (DOCX)")
        print("3) Esci")
        choice = input("Seleziona un'opzione (1-3): ").strip()

        if choice == "1":
            # Lancia lo script di import. Chiediamo se l'utente vuole passare file
            sql = input(
                "Percorso file SQL (lascia vuoto per scegliere interattivamente): "
            ).strip()
            if sql:
                safe_run_module_main("import_articoli_to_sqlite", [sql])
            else:
                safe_run_module_main("import_articoli_to_sqlite", [])

        elif choice == "2":
            db = input("Database (default: articoli.db): ").strip() or "articoli.db"
            # Passiamo il nome del DB come primo argomento
            safe_run_module_main("esplora_articoli", [db])

        elif choice == "3":
            print("Uscita. A presto!")
            return

        else:
            print("Scelta non valida, riprova.")


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point principale. Se vengono passati argomenti, prova a interpretare
    comandi rapidi per saltare il menu (es. `--import file.sql` o `--export db.db`)."""
    argv = list(argv) if argv is not None else sys.argv[1:]

    if argv:
        # Simple dispatch for direct invocation
        # --import can be passed with or without a filename
        if argv[0] in ("--import", "import"):
            safe_run_module_main("import_articoli_to_sqlite", argv[1:])
            return 0
        if argv[0] in ("--export", "export"):
            # support optional db path
            dbarg = argv[1:] if len(argv) >= 2 else []
            safe_run_module_main("esplora_articoli", dbarg)
            return 0

    try:
        prompt_menu()
        return 0
    except KeyboardInterrupt:
        print("\nInterrotto dall'utente. Arrivederci.")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
