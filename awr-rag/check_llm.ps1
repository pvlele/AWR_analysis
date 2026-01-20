# check_llm.ps1

# Base URL for the Chat Completions API
$Url = "http://localhost:12434/v1/chat/completions"

# Configuration
$Model = "ai/gemma3:4B-Q4_0"
$MessageContent = "Hello, are you running?"
$MaxTokens = 100

# Define headers here
$Headers = @{
    # "Authorization" = "Bearer your-token"
}

# Payload
$Body = @{
    model      = $Model
    messages   = @(
        @{
            role    = "user"
            content = $MessageContent
        }
    )
    max_tokens = $MaxTokens
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
