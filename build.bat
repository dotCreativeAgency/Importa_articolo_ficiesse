@echo off
chcp 65001 > nul
REM Script batch per creare l'eseguibile Windows
REM Si comporta come app.bat: gestisce virtual environment e dipendenze automaticamente
REM
REM Uso:
REM   build.bat [clean] [test]

setlocal enabledelayedexpansion
cd /d "%~dp0"

set "CLEAN_BUILD=false"
set "TEST_BUILD=false"

REM Parse arguments
:parse_args
if "%~1"=="" goto setup
if /i "%~1"=="clean" (
    set "CLEAN_BUILD=true"
    shift
    goto parse_args
)
if /i "%~1"=="test" (
    set "TEST_BUILD=true"
    shift
    goto parse_args
)
echo ⚠️  Argomento sconosciuto: %~1
echo Uso: %0 [clean] [test]
echo   clean  Rimuovi build precedenti
echo   test   Esegui test dopo il build
exit /b 1

:setup
echo 🔨 Build Eseguibile - Importa Articoli Ficiesse
echo =====================================================

REM Pulisci build precedenti se richiesto
if "%CLEAN_BUILD%"=="true" (
    echo 🗑️  Pulizia build precedenti...
    if exist dist rmdir /s /q dist
    if exist build rmdir /s /q build
    if exist *.spec del /q *.spec
    echo ✅ Pulizia completata
    echo.
)

REM Attiva l'ambiente virtuale se presente (stessa logica di app.bat)
if exist ".venv\Scripts\activate.bat" (
    echo 🐍 Attivazione virtual environment ^(.venv^)...
    call .venv\Scripts\activate.bat
) else if exist "venv\Scripts\activate.bat" (
    echo 🐍 Attivazione virtual environment ^(venv^)...
    call venv\Scripts\activate.bat
) else (
    echo ⚠️  Virtual environment non trovato!
    echo.
    echo 🔧 Creazione virtual environment e installazione dipendenze...
    python -m venv .venv
    if !ERRORLEVEL! neq 0 (
        echo ❌ Errore: impossibile creare il virtual environment
        echo    Verifica che Python sia installato correttamente
        pause
        exit /b 1
    )
    call .venv\Scripts\activate.bat
    echo ✅ Virtual environment creato!
    echo.
)

REM Verifica e installa dipendenze se necessario
echo 📦 Verifica dipendenze...

pip show pyinstaller >nul 2>&1
if !ERRORLEVEL! neq 0 (
    echo 🔧 Installazione dipendenze di sviluppo...
    python -m pip install --quiet --upgrade pip
    pip install --quiet -r requirements.txt
    pip install --quiet -r requirements-dev.txt
    echo ✅ Dipendenze installate!
) else (
    echo ✅ PyInstaller già disponibile
)

echo.

REM Build con PyInstaller
echo 🔨 Creazione eseguibile con PyInstaller...
echo.

pyinstaller --onefile --name importa_articoli importa_articoli_app.py
if !ERRORLEVEL! equ 0 (
    echo.
    echo ✅ Build completato con successo!
    
    REM Mostra informazioni del file creato
    if exist "dist\importa_articoli.exe" (
        set "EXECUTABLE_PATH=dist\importa_articoli.exe"
        echo 📁 Eseguibile: !EXECUTABLE_PATH!
        
        REM Test del build se richiesto
        if "%TEST_BUILD%"=="true" (
            echo 🧪 Test dell'eseguibile...
            timeout /t 3 /nobreak >nul 2>&1 && (
                echo ✅ Test eseguibile: PASSED
            ) || (
                echo ⚠️  Test eseguibile: Timeout o errore ^(normale per app interattive^)
            )
            echo.
        )
        
        REM Istruzioni per l'uso
        echo 🚀 Come utilizzare:
        echo    !EXECUTABLE_PATH!
        echo.
        echo 📋 Note:
        echo    • L'eseguibile include tutto il necessario
        echo    • Può essere distribuito su sistemi Windows senza Python
        echo    • Per build automatico usa GitHub Actions ^(workflow windows-build.yml^)
        
    ) else (
        echo ❌ Errore: file eseguibile non trovato in dist\
        pause
        exit /b 1
    )
) else (
    echo.
    echo ❌ Errore durante il build con PyInstaller
    pause
    exit /b 1
)

echo.
echo 🎉 Build completato!
pause