# Get the absolute path to the project root (assuming awr-rag is one level deep)
$ScriptDir = $PSScriptRoot
# $ProjectRoot = Split-Path -Parent $ScriptDir # Old logic assuming parent venv
$VenvPython = Join-Path $ScriptDir ".venv\Scripts\python.exe"

# check if python exists in the expected location
if (-not (Test-Path $VenvPython)) {
    Write-Host "Error: Virtual environment python not found at $VenvPython" -ForegroundColor Red
    exit 1
}

Write-Host "Running CLI using: $VenvPython"
Set-Location $ScriptDir
# Run the module properly propagating arguments
& $VenvPython -m app.cli $args
