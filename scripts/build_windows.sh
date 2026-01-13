#!/usr/bin/env bash
set -euo pipefail
# Build a one-file executable with PyInstaller
# Usage: ./scripts/build_windows.sh

pyinstaller --onefile --name importa_articoli importa_articoli_app.py

echo "Built: dist/importa_articoli"