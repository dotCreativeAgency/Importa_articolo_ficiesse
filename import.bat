@echo off
REM Script per avviare l'import interattivo
REM Mostra un menu per scegliere quale file importare

cd /d "%~dp0"

REM Attiva l'ambiente virtuale se presente
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Avvia lo script senza argomenti -> modalita' interattiva
python import_articoli_to_sqlite.py

pause
