@echo off
REM Script per avviare l'import interattivo
REM Mostra un menu per scegliere quale file importare

cd /d "%~dp0"

REM Attiva l'ambiente virtuale se presente
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Avvia il launcher e apre il menu Import senza richiedere percorso file
python importa_articoli_app.py import

pause
