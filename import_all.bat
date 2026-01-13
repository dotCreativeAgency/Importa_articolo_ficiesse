@echo off
REM Script per importare tutti i file SQL dalla cartella import
REM 
REM Uso:
REM   1. Posiziona i file SQL nella cartella 'import\'
REM   2. Doppio click su import_all.bat oppure esegui da cmd

setlocal enabledelayedexpansion

cd /d "%~dp0"

REM Nome del database SQLite di destinazione
set DB_NAME=articoli.db

REM Cartella con i file da importare
set IMPORT_DIR=%~dp0import

echo.
echo ========================================
echo  Script di Importazione MySQL - SQLite
echo ========================================
echo.

REM Verifica se la cartella import esiste
if not exist "%IMPORT_DIR%" (
    echo Creazione cartella import...
    mkdir "%IMPORT_DIR%"
)

REM Cerca tutti i file SQL nella cartella import
set FILE_COUNT=0
for %%F in ("%IMPORT_DIR%\*.sql") do (
    set /a FILE_COUNT+=1
)

if %FILE_COUNT%==0 (
    echo [ERRORE] Nessun file SQL trovato nella cartella 'import\'
    echo.
    echo Posiziona i file SQL nella cartella import\ con nomi come:
    echo   - t_articoli.sql
    echo   - t_articoli_001.sql, t_articoli_002.sql, ecc.
    echo.
    pause
    exit /b 1
)

echo Trovati %FILE_COUNT% file SQL
echo.
set /p CONFIRM="Vuoi importare tutti i file nel database '%DB_NAME%'? (S/N): "
if /i not "%CONFIRM%"=="S" (
    echo Operazione annullata.
    pause
    exit /b 0
)

echo.
echo Inizio importazione...
echo ========================================

REM Contatori
set CURRENT=0

REM Importa ogni file
for %%F in ("%IMPORT_DIR%\*.sql") do (
    set /a CURRENT+=1
    echo.
    echo [!CURRENT!/%FILE_COUNT%] Importazione di: %%~nxF
    echo ----------------------------------------
    
    python import_articoli_to_sqlite.py "%%~nxF" "%DB_NAME%"
    
    if errorlevel 1 (
        echo [ERRORE] Errore durante l'importazione di %%F
        set /p CONTINUE="Vuoi continuare con i file rimanenti? (S/N): "
        if /i not "!CONTINUE!"=="S" (
            echo Importazione interrotta.
            pause
            exit /b 1
        )
    )
)

echo.
echo ========================================
echo Importazione completata!
echo ========================================
echo File processati: %FILE_COUNT%
echo.

REM Mostra statistiche finali
echo Statistiche finali del database:
python -c "import sqlite3; conn=sqlite3.connect('%DB_NAME%'); cursor=conn.cursor(); cursor.execute('SELECT COUNT(*) FROM t_articoli'); print(f'  Totale articoli: {cursor.fetchone()[0]}'); conn.close()"

echo.
echo Database '%DB_NAME%' pronto per l'uso!
echo.
pause
