# 🔨 Build Guide - Creazione Eseguibili

Questa guida spiega come creare eseguibili autonomi dell'applicazione "Importa Articoli Ficiesse" per diverse piattaforme.

## 🚀 Quick Start

### Linux/macOS
```bash
# Build completo con gestione automatica ambiente
./build.sh

# Build con pulizia preventiva
./build.sh --clean

# Build con test
./build.sh --clean --test
```

### Windows
```batch
REM Build completo con gestione automatica ambiente
build.bat

REM Build con pulizia preventiva  
build.bat clean

REM Build con test
build.bat clean test
```

## 📋 Panoramica

L'applicazione supporta tre metodi di build:

1. **🏆 RACCOMANDATO**: Script unificati `build.sh`/`build.bat`
2. **🤖 AUTOMATICO**: GitHub Actions per Windows
3. **⚙️ MANUALE**: Script legacy nella cartella `scripts/`

## 🔧 Metodi di Build

### 1. Script Unificati (RACCOMANDATO)

I nuovi script [`build.sh`](build.sh) e [`build.bat`](build.bat) replicano il comportamento di [`app.sh`](app.sh)/[`app.bat`](app.bat):

**Caratteristiche:**
- ✅ Gestione automatica virtual environment
- ✅ Installazione automatica dipendenze
- ✅ Validazione prerequisiti
- ✅ Output dettagliato con emoji
- ✅ Opzioni per pulizia e test
- ✅ Cross-platform consistency

**Comportamento:**
1. Cerca virtual environment esistente (`.venv` o `venv`)
2. Se non trovato, lo crea automaticamente
3. Attiva l'ambiente e verifica dipendenze
4. Installa PyInstaller e requirements se necessario
5. Esegue build con PyInstaller
6. Mostra statistiche e istruzioni d'uso

### 2. GitHub Actions (AUTOMATICO)

Il workflow [`.github/workflows/windows-build.yml`](.github/workflows/windows-build.yml) crea automaticamente l'eseguibile Windows:

**Trigger:**
- Push su branch `main`
- Manuale tramite `workflow_dispatch`

**Processo:**
1. Setup Windows runner con Python 3.11
2. Installazione dipendenze da `requirements.txt` + `requirements-dev.txt`
3. Build con PyInstaller
4. Upload come artifact `importa_articoli-windows`

**Come usare:**
1. Vai su **Actions** nel repository GitHub
2. Seleziona "Build Windows executable" 
3. Clicca "Run workflow"
4. Scarica l'artifact al completamento

### 3. Script Legacy (MANUALE)

Script semplificati in [`scripts/`](scripts/) per uso avanzato:

- [`scripts/build_windows.sh`](scripts/build_windows.sh) - Linux build
- [`scripts/build_windows.ps1`](scripts/build_windows.ps1) - PowerShell build

**⚠️ Limitazioni:**
- Non gestiscono virtual environment
- Non installano dipendenze
- Assumono PyInstaller già configurato

## 📦 Output

### Linux
```
dist/importa_articoli          # Eseguibile Linux (~7MB)
```

### Windows  
```
dist/importa_articoli.exe      # Eseguibile Windows (~8MB)
```

### File Temporanei
```
build/                         # File temporanei PyInstaller
importa_articoli.spec         # Specifica build PyInstaller
```

## 🧪 Testing degli Eseguibili

Gli script supportano testing automatico con `--test` flag:

```bash
# Linux
./build.sh --test

# Windows
build.bat test
```

Il test verifica che l'eseguibile:
- Si avvii correttamente
- Mostri il menu principale
- Risponda ai comandi (con timeout per app interattive)

## 🔧 Troubleshooting

### Problema: PyInstaller non trovato
```bash
# Soluzione: Installa dipendenze di sviluppo
pip install -r requirements-dev.txt
```

### Problema: Virtual environment non creato
```bash
# Linux: Installa python3-venv
sudo apt install python3-venv

# Windows: Reinstalla Python con "Add to PATH"
```

### Problema: Build fallisce su Windows
1. Verifica che Python sia nel PATH
2. Usa PowerShell come Administrator se necessario
3. Controlla antivirus (può bloccare PyInstaller)

### Problema: Eseguibile troppo grande
Il build include tutto Python e dipendenze (~7-8MB è normale). Per ridurre:
```bash
# Usa --exclude-module per librerie non necessarie
pyinstaller --onefile --exclude-module tkinter importa_articoli_app.py
```

## 🚀 Distribuzione

### Linux
```bash
# L'eseguibile è autonomo
./dist/importa_articoli

# Può essere copiato su qualsiasi sistema Linux x64
scp dist/importa_articoli user@target:/path/to/
```

### Windows
```batch
REM L'eseguibile è autonomo
dist\importa_articoli.exe

REM Può essere distribuito senza Python installato
copy dist\importa_articoli.exe \\target\path\
```

## 📋 Best Practices

1. **Usa script unificati** (`build.sh`/`build.bat`) per consistency
2. **Testa sempre** con `--test` flag prima della distribuzione
3. **Pulisci build** con `--clean` se cambi dipendenze
4. **Per Windows production**: usa GitHub Actions per ambiente pulito
5. **Versioning**: tagga releases per tracking builds

## 🔗 File Correlati

- [`build.sh`](build.sh) - Script build Linux/macOS
- [`build.bat`](build.bat) - Script build Windows  
- [`app.sh`](app.sh) - Reference per gestione ambiente
- [`importa_articoli_app.py`](importa_articoli_app.py) - Entry point applicazione
- [`requirements-dev.txt`](requirements-dev.txt) - Dipendenze build
- [`.github/workflows/windows-build.yml`](.github/workflows/windows-build.yml) - CI/CD Windows