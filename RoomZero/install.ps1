$ErrorActionPreference = "Stop"

param(
    [switch]$WithBuilder
)

Write-Host "Creating virtual environment..."
python -m venv .venv

Write-Host "Activating virtual environment..."
& .\.venv\Scripts\Activate.ps1

Write-Host "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

if ($WithBuilder) {
    Write-Host "Installing installer build tooling..."
    pip install pyinstaller
}

Write-Host "Install complete."
if ($WithBuilder) {
    Write-Host "You can now run: .\build_installer.ps1"
}
