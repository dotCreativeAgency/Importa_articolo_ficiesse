@echo off
REM Script per avviare l'applicazione unificata Import & Esplora Articoli
REM Mostra un menu principale per scegliere tra importazione e esplorazione
REM
REM Uso:
REM   app.bat

cd /d "%~dp0"

REM Attiva l'ambiente virtuale se presente
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo Attenzione: Virtual environment non trovato!
    echo.
    echo Creazione virtual environment e installazione dipendenze...
    python -m venv .venv
    
    if errorlevel 1 (
        echo Errore: impossibile creare il virtual environment
        pause
        exit /b 1
    )
    
    call .venv\Scripts\activate.bat
    pip install -r requirements.txt
    echo.
    echo Virtual environment creato e dipendenze installate!
    echo.
)

REM Avvia il launcher unificato (menu principale)
python importa_articoli_app.py

pause
