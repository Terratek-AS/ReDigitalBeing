param(
    [switch]$WithBuilder
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

Write-Host "Starting RoomZero installation bootstrap..."

if (-not (Test-Path ".\requirements.txt")) {
    throw "requirements.txt not found. Run this script from the RoomZero directory."
}

try {
    $policy = Get-ExecutionPolicy -Scope Process
    if ($policy -eq "Restricted") {
        Write-Warning "PowerShell execution policy is Restricted for this process."
        Write-Warning "If activation fails, run: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass"
    }
}
catch {
    Write-Warning "Could not read execution policy. Continuing..."
}

Require-Command -Name "python"

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    Write-Host "Virtual environment not found. Creating .venv..."
    python -m venv .venv
}
else {
    Write-Host "Virtual environment already exists. Reusing .venv..."
}

Write-Host "Activating virtual environment..."
& .\.venv\Scripts\Activate.ps1

Require-Command -Name "pip"

Write-Host "Installing dependencies..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if ($WithBuilder) {
    Write-Host "Installing installer build tooling..."
    python -m pip install pyinstaller
}

Write-Host "Install complete."
Write-Host "Run app: .\run.ps1"
if ($WithBuilder) {
    Write-Host "Build installer: .\build_installer.ps1"
}
