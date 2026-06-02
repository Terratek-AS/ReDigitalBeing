param(
    [string]$BaseUrl = "http://127.0.0.1:8000"
)

$ErrorActionPreference = "Stop"

function Invoke-RequestStatus {
    param(
        [string]$Method,
        [string]$Path,
        [object]$Body = $null
    )

    $url = "$BaseUrl$Path"
    $jsonBody = $null
    if ($null -ne $Body) {
        $jsonBody = $Body | ConvertTo-Json -Depth 10 -Compress
    }

    try {
        if ($null -ne $jsonBody) {
            $response = Invoke-WebRequest -Uri $url -Method $Method -ContentType "application/json" -Body $jsonBody -MaximumRedirection 0 -UseBasicParsing -ErrorAction Stop
        }
        else {
            $response = Invoke-WebRequest -Uri $url -Method $Method -MaximumRedirection 0 -UseBasicParsing -ErrorAction Stop
        }
        return [int]$response.StatusCode
    }
    catch {
        if ($_.Exception.Response -and $_.Exception.Response.StatusCode) {
            return [int]$_.Exception.Response.StatusCode
        }
        throw
    }
}

function Assert-StatusCode {
    param(
        [string]$Method,
        [string]$Path,
        [int[]]$ExpectedCodes,
        [object]$Body = $null
    )

    $status = Invoke-RequestStatus -Method $Method -Path $Path -Body $Body
    if ($ExpectedCodes -notcontains $status) {
        throw "FAILED: $Method $Path -> got $status, expected one of: $($ExpectedCodes -join ', ')"
    }
    Write-Host "PASS: $Method $Path -> $status"
}

Write-Host "Running RoomZero API smoke checks against $BaseUrl"

# Core health + UI/docs
Assert-StatusCode -Method "GET" -Path "/health" -ExpectedCodes @(200)
Assert-StatusCode -Method "GET" -Path "/ui" -ExpectedCodes @(200)
Assert-StatusCode -Method "GET" -Path "/docs" -ExpectedCodes @(200)
Assert-StatusCode -Method "GET" -Path "/static" -ExpectedCodes @(200, 307)

# Core data endpoints
Assert-StatusCode -Method "GET" -Path "/persona" -ExpectedCodes @(200)
Assert-StatusCode -Method "GET" -Path "/state" -ExpectedCodes @(200)
Assert-StatusCode -Method "GET" -Path "/memory/recent" -ExpectedCodes @(200)
Assert-StatusCode -Method "GET" -Path "/logs/recent" -ExpectedCodes @(200)

# Research/tester network reads
Assert-StatusCode -Method "GET" -Path "/research/questions" -ExpectedCodes @(200)
Assert-StatusCode -Method "GET" -Path "/research/jobs" -ExpectedCodes @(200)
Assert-StatusCode -Method "GET" -Path "/sources/queue" -ExpectedCodes @(200)
Assert-StatusCode -Method "GET" -Path "/sources/approved" -ExpectedCodes @(200)
Assert-StatusCode -Method "GET" -Path "/feedback/stats" -ExpectedCodes @(200)
Assert-StatusCode -Method "GET" -Path "/testers" -ExpectedCodes @(200)

# Expected non-200 behaviors
Assert-StatusCode -Method "GET" -Path "/" -ExpectedCodes @(404)
Assert-StatusCode -Method "GET" -Path "/memory" -ExpectedCodes @(405)

# POST happy paths
Assert-StatusCode -Method "POST" -Path "/chat" -ExpectedCodes @(200) -Body @{
    message = "hello from smoke api"
}
Assert-StatusCode -Method "POST" -Path "/memory" -ExpectedCodes @(200) -Body @{
    content = "automation semantic memory"
    category = "semantic"
    importance = 0.6
    tags = @("automation","smoke")
    source = "automation"
}
Assert-StatusCode -Method "POST" -Path "/feedback/session" -ExpectedCodes @(200) -Body @{
    tester_id = "automation-tester"
    session_id = "automation-session"
    realism_score = 8
    coherence_score = 8
    memory_score = 7
    emotional_presence_score = 7
    ethical_safety_score = 9
    usefulness_score = 8
    uncanny_score = 3
    trust_score = 8
}
Assert-StatusCode -Method "POST" -Path "/sources/submit" -ExpectedCodes @(200) -Body @{
    title = "Automation Source"
    url_or_reference = "https://example.com/automation"
    submitted_by = "automation"
    category = "other"
    claimed_relevance = "smoke"
}
Assert-StatusCode -Method "POST" -Path "/research/jobs" -ExpectedCodes @(200) -Body @{
    name = "Automation Job"
    topic = "agent memory"
    category = "other"
    query = "agent memory"
    schedule = "manual"
    created_by = "automation"
}
Assert-StatusCode -Method "POST" -Path "/research/questions" -ExpectedCodes @(200) -Body @{
    question = "How to improve automation reliability?"
    category = "other"
    submitted_by = "automation"
}
Assert-StatusCode -Method "POST" -Path "/testers/invite" -ExpectedCodes @(200) -Body @{
    role = "tester"
    issued_by = "automation"
}

# POST negative paths (validation errors expected)
Assert-StatusCode -Method "POST" -Path "/chat" -ExpectedCodes @(422) -Body @{}
Assert-StatusCode -Method "POST" -Path "/memory" -ExpectedCodes @(200) -Body @{
    content = "minimal valid memory payload"
}
Assert-StatusCode -Method "POST" -Path "/feedback/session" -ExpectedCodes @(422) -Body @{
    tester_id = "automation-tester"
}
Assert-StatusCode -Method "POST" -Path "/sources/submit" -ExpectedCodes @(422) -Body @{
    title = "Missing URL"
}
Assert-StatusCode -Method "POST" -Path "/research/jobs" -ExpectedCodes @(422) -Body @{
    name = "Incomplete Job"
}
Assert-StatusCode -Method "POST" -Path "/research/questions" -ExpectedCodes @(422) -Body @{
    category = "other"
}
Assert-StatusCode -Method "POST" -Path "/testers/invite" -ExpectedCodes @(200) -Body @{
    role = "tester"
}

Write-Host "All smoke checks passed."
