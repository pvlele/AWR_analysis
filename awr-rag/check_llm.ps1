# check_llm.ps1

# Base URL from config
# Base URL from config
$Url = "http://localhost:12435/v1/chat/completions"

# Configuration from config
$Model = "llama3.1:8B-Q4_K_M"
$MessageContent = "Hello, are you running?"
# $MaxTokens = 100 # Moved to options

# Define headers here
$Headers = @{
    "Authorization" = "Bearer my-token1"
    "User-Agent"    = "AWR-RAG-Check/1.0"
}

# Payload (Chat format matching analyzer.py)
$Body = @{
    model    = $Model
    messages = @(
        @{
            role    = "user"
            content = $MessageContent
        }
    )
    stream   = $false
    options  = @{
        num_predict = 100
    }
}

$JsonBody = $Body | ConvertTo-Json -Depth 3

Write-Host "Sending POST request to $Url..."
Write-Host "Payload: $JsonBody"

try {
    # Send a request to the server
    $response = Invoke-RestMethod -Uri $Url -Method Post -Headers $Headers -Body $JsonBody -ContentType "application/json" -ErrorAction Stop
    
    Write-Host "✅ Response Received:" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 5 | Write-Host
} catch {
    Write-Host "❌ Request Failed: $_" -ForegroundColor Red
}
