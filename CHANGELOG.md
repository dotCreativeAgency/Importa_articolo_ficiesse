# Changelog

Tutte le modifiche rilevanti al progetto vengono elencate qui.

## v0.2.0 — 2026-01-14

### Build e Distribuzione
- ✨ Nuovo script unificato `build.sh`/`build.bat` per creazione eseguibili
- ✨ Gestione automatica virtual environment e dipendenze (come `app.sh`)
- ✨ Opzioni avanzate: `--clean` (pulizia) e `--test` (validazione build)
- 📖 Nuova documentazione completa: `BUILD.md`
- 🔧 Script legacy deprecati con warning e redirect

### Miglioramenti
- ✅ Build process semplificato e user-friendly
- ✅ Cross-platform consistency (Linux/Windows)
- ✅ Documentazione README aggiornata con sezione build
- ✅ Output dettagliato con emoji e statistiche

## v0.1.0 — 2026-01-13

- Aggiunta barra di progresso per import (`tqdm`) per seguire l'avanzamento
- Nuove opzioni CLI in `esplora_articoli.py`: `--export-all`, `--export-only-new`, `--export-limit`
- Export: un file DOCX per articolo; aggiunta colonna `esportato` per tracciare gli articoli esportati
- Parser SQL estratto in `lib/parser.py` e coperto da test unitari
- Aggiunti test di integrazione (export multiplo, export-only-new) e test di import
- CI e qualità: GitHub Actions, `black`, `flake8`, `pre-commit` configurati
- Migliorie UX e messaggi di log
