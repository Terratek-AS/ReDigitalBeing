param(
    [switch]$ProbeHealth
)

Write-Host "Checking Docker availability..."
try {
    docker version | Out-Null
} catch {
    Write-Host "Docker does not appear to be available. Please start Docker Desktop or ensure docker is on PATH." -ForegroundColor Yellow
    exit 2
}

Write-Host "Bringing up compose stack (build + detached)..."
docker compose -f "docker-compose.yml" up --build -d

Write-Host "Application should be available at http://127.0.0.1:8000"

if ($ProbeHealth) {
    Write-Host "Probing /health endpoint..."
    $tries = 0
    while ($tries -lt 6) {
        try {
            $r = Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:8000/health" -TimeoutSec 5
            if ($r.StatusCode -eq 200) {
                Write-Host "Health OK: $($r.Content)"
                exit 0
            }
        } catch {
            Start-Sleep -Seconds 2
            $tries++
        }
    }
    Write-Host "Health probe failed after retries." -ForegroundColor Red
    docker compose -f "docker-compose.yml" logs --no-color --tail 200
    exit 1
}

exit 0
