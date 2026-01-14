# PowerShell build script for Windows runner (Legacy script)
# RECOMMENDED: Use GitHub Actions workflow for automated Windows builds
# Usage (PowerShell): ./scripts/build_windows.ps1

Write-Host "⚠️  DEPRECATO: Usa GitHub Actions per build automatico Windows" -ForegroundColor Yellow
Write-Host "Workflow: .github/workflows/windows-build.yml" -ForegroundColor Cyan
Write-Host "Procedendo con build locale..." -ForegroundColor Yellow
Write-Host ""

# Verifica che PyInstaller sia disponibile
try {
    pyinstaller --version | Out-Null
} catch {
    Write-Host "❌ PyInstaller non trovato. Installa con:" -ForegroundColor Red
    Write-Host "   pip install -r requirements-dev.txt" -ForegroundColor White
    exit 1
}

pyinstaller --onefile --name importa_articoli importa_articoli_app.py

if (Test-Path "dist/importa_articoli.exe") {
    Write-Host ""
    Write-Host "✅ Build completato: dist/importa_articoli.exe" -ForegroundColor Green
    Write-Host "💡 Per distribuzione usa GitHub Actions" -ForegroundColor Cyan
} else {
    Write-Host "❌ Errore: build fallito" -ForegroundColor Red
    exit 1
}