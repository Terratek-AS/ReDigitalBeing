$ErrorActionPreference = "Stop"

Write-Host "Starting RoomZero Windows packaging..."

if (-not (Test-Path ".\requirements.txt")) {
    throw "requirements.txt not found. Run this script from the RoomZero directory."
}

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    Write-Host "Virtual environment not found. Creating..."
    python -m venv .venv
}

Write-Host "Activating virtual environment..."
& .\.venv\Scripts\Activate.ps1

Write-Host "Installing build dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

Write-Host "Cleaning previous build artifacts..."
if (Test-Path ".\build") { Remove-Item ".\build" -Recurse -Force }
if (Test-Path ".\dist") { Remove-Item ".\dist" -Recurse -Force }

Write-Host "Building RoomZero executable with PyInstaller..."
pyinstaller `
  --name RoomZero `
  --onefile `
  --add-data "data;data" `
  --add-data "app\static;app\static" `
  --hidden-import uvicorn.logging `
  --hidden-import uvicorn.loops `
  --hidden-import uvicorn.loops.auto `
  --hidden-import uvicorn.protocols `
  --hidden-import uvicorn.protocols.http `
  --hidden-import uvicorn.protocols.http.auto `
  --hidden-import uvicorn.protocols.websockets `
  --hidden-import uvicorn.protocols.websockets.auto `
  --hidden-import uvicorn.lifespan `
  --hidden-import uvicorn.lifespan.on `
  --collect-all fastapi `
  --collect-all pydantic `
  --collect-all starlette `
  app\main.py

if (-not (Test-Path ".\dist\RoomZero.exe")) {
    throw "Build failed: dist\RoomZero.exe was not created."
}

Write-Host "PyInstaller build complete: .\dist\RoomZero.exe"
Write-Host ""
Write-Host "To build an installer (Setup.exe), install Inno Setup and run:"
Write-Host '  iscc .\installer\RoomZero.iss'
