param(
    [string]$ServerHost = "127.0.0.1",
    [int]$Port = 8000,
    [int]$StartupTimeoutSeconds = 30
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$baseUrl = "http://$ServerHost`:$Port"

function Ensure-Venv {
    if (-not (Test-Path ".\.venv\Scripts\Activate.ps1")) {
        throw "Virtual environment not found. Run .\install.ps1 first."
    }
    & .\.venv\Scripts\Activate.ps1
}

function Wait-ForHealth {
    param(
        [string]$Url,
        [int]$TimeoutSeconds
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        try {
            $r = Invoke-WebRequest -Uri "$Url/health" -Method GET -UseBasicParsing -ErrorAction Stop
            if ([int]$r.StatusCode -eq 200) {
                Write-Host "Server health check OK."
                return
            }
        }
        catch {
            Start-Sleep -Milliseconds 500
        }
    }

    throw "Server did not become healthy within $TimeoutSeconds seconds."
}

$startedHere = $false
$serverProcess = $null

try {
    Write-Host "Step 1/4: Activate venv"
    Ensure-Venv

    Write-Host "Step 2/4: Run tests"
    python -m pytest -q
    if ($LASTEXITCODE -ne 0) {
        throw "Pytest failed."
    }

    Write-Host "Step 3/4: Ensure server running"
    $healthUp = $false
    try {
        $ping = Invoke-WebRequest -Uri "$baseUrl/health" -Method GET -UseBasicParsing -ErrorAction Stop
        if ([int]$ping.StatusCode -eq 200) {
            $healthUp = $true
            Write-Host "Detected existing running server."
        }
    }
    catch {
        $healthUp = $false
    }

    if (-not $healthUp) {
        Write-Host "No running server detected; starting temporary uvicorn process..."
        $serverProcess = Start-Process -FilePath ".\.venv\Scripts\python.exe" `
            -ArgumentList "-m uvicorn app.main:app --host $ServerHost --port $Port" `
            -PassThru -WindowStyle Hidden
        $startedHere = $true
        Wait-ForHealth -Url $baseUrl -TimeoutSeconds $StartupTimeoutSeconds
    }

    Write-Host "Step 4/4: API smoke checks"
    & "$PSScriptRoot\smoke_api.ps1" -BaseUrl $baseUrl
    if ($LASTEXITCODE -ne 0) {
        throw "Smoke API checks failed."
    }

    Write-Host ""
    Write-Host "VERIFY RESULT: PASS"
}
catch {
    Write-Error $_
    Write-Host ""
    Write-Host "VERIFY RESULT: FAIL"
    exit 1
}
finally {
    if ($startedHere -and $serverProcess -and -not $serverProcess.HasExited) {
        Write-Host "Stopping temporary uvicorn process..."
        Stop-Process -Id $serverProcess.Id -Force
    }
}
