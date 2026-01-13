# PowerShell build script for Windows runner
# Usage (PowerShell): ./scripts/build_windows.ps1

pyinstaller --onefile --name importa_articoli importa_articoli_app.py
Write-Host "Built: dist/importa_articoli.exe"