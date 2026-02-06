@echo off
chcp 65001 > nul
REM Script per avviare l'esplorazione articoli con il virtual environment
REM
REM Uso:
REM   esplora.bat [database.db]
REM
REM Esempio:
REM   esplora.bat              # Usa articoli.db di default
REM   esplora.bat mio_db.db    # Usa database specificato

setlocal enabledelayedexpansion

cd /d "%~dp0"

REM Nome del database (default: articoli.db)
if "%~1"=="" (
    set DB_NAME=articoli.db
) else (
    set DB_NAME=%~1
)

REM Verifica se esiste il virtual environment
if not exist "venv" (
    echo [AVVISO] Virtual environment non trovato!
    echo.
    echo Creazione virtual environment e installazione dipendenze...
    python -m venv venv
    
    if errorlevel 1 (
        echo [ERRORE] Impossibile creare il virtual environment
        pause
        exit /b 1
    )
    
    call venv\Scripts\activate.bat
    pip install python-docx htmldocx beautifulsoup4
    echo.
    echo Virtual environment creato e dipendenze installate!
    echo.
) else (
    call venv\Scripts\activate.bat
)

REM Verifica se esiste il database di default
if not exist "articoli.db" (
    echo [ERRORE] Database 'articoli.db' non trovato!
    echo.
    echo Usa prima lo script di importazione (o posiziona il DB nella cartella):
    echo    import.bat
    pause
    exit /b 1
)

REM Avvia il launcher in modalità Export (non chiede il DB)
python importa_articoli_app.py export

pause
