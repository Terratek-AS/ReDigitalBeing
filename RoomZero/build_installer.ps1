param(
    [switch]$BuildInstaller,
    [string]$AppVersion = "1.0.0"
)

$ErrorActionPreference = "Stop"

function Require-Command {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name
    )

    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command '$Name' was not found in PATH."
    }
}

Write-Host "Starting RoomZero Windows packaging..."

if (-not (Test-Path ".\requirements.txt")) {
    throw "requirements.txt not found. Run this script from the RoomZero directory."
}

Require-Command -Name "python"

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    Write-Host "Virtual environment not found. Creating..."
    python -m venv .venv
}

Write-Host "Activating virtual environment..."
& .\.venv\Scripts\Activate.ps1

Write-Host "Installing build dependencies..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller

Write-Host "Cleaning previous build artifacts..."
if (Test-Path ".\build") { Remove-Item ".\build" -Recurse -Force }
if (Test-Path ".\dist") { Remove-Item ".\dist" -Recurse -Force }

Write-Host "Building RoomZero executable with PyInstaller..."
python -m PyInstaller `
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

if ($BuildInstaller) {
    Write-Host "Building Inno Setup installer..."
    $iscc = Get-Command iscc -ErrorAction SilentlyContinue
    if (-not $iscc) {
        throw "Inno Setup compiler (iscc) not found in PATH. Install Inno Setup or run without -BuildInstaller."
    }

    & $iscc.Source "/DMyAppVersion=$AppVersion" ".\installer\RoomZero.iss"

    if (-not (Test-Path ".\dist\installer\RoomZero-Setup.exe")) {
        throw "Installer build failed: .\dist\installer\RoomZero-Setup.exe was not created."
    }

    Write-Host "Installer build complete: .\dist\installer\RoomZero-Setup.exe"
}
else {
    Write-Host ""
    Write-Host "To build installer too, run:"
    Write-Host "  .\build_installer.ps1 -BuildInstaller -AppVersion $AppVersion"
}
