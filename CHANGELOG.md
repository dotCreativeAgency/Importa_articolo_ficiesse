# Changelog

Tutte le modifiche rilevanti al progetto vengono elencate qui.

## v0.1.0 — 2026-01-13

- Aggiunta barra di progresso per import (`tqdm`) per seguire l'avanzamento
- Nuove opzioni CLI in `esplora_articoli.py`: `--export-all`, `--export-only-new`, `--export-limit`
- Export: un file DOCX per articolo; aggiunta colonna `esportato` per tracciare gli articoli esportati
- Parser SQL estratto in `lib/parser.py` e coperto da test unitari
- Aggiunti test di integrazione (export multiplo, export-only-new) e test di import
- CI e qualità: GitHub Actions, `black`, `flake8`, `pre-commit` configurati
- Migliorie UX e messaggi di log
