# Personal Recipe Intelligence - Development Server (Windows PowerShell)
# Usage: .\scripts\dev.ps1

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Personal Recipe Intelligence" -ForegroundColor Cyan
Write-Host "  Development Server (Windows)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment if exists
if (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "[*] Activating Python virtual environment..." -ForegroundColor Yellow
    & .\.venv\Scripts\Activate.ps1
}

# Start backend in background
Write-Host "[*] Starting Backend API (port 8000)..." -ForegroundColor Yellow
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    if (Test-Path ".venv\Scripts\Activate.ps1") {
        & .\.venv\Scripts\Activate.ps1
    }
    python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload
}
Write-Host "  Backend started (Job ID: $($backendJob.Id))" -ForegroundColor Green

# Wait for backend to be ready
Write-Host "[*] Waiting for backend to be ready..." -ForegroundColor Yellow
$maxAttempts = 30
$attempt = 0
while ($attempt -lt $maxAttempts) {
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "  Backend is ready!" -ForegroundColor Green
            break
        }
    } catch {
        $attempt++
        Start-Sleep -Seconds 1
    }
}

if ($attempt -ge $maxAttempts) {
    Write-Host "[WARNING] Backend may not be ready yet" -ForegroundColor Yellow
}

# Start frontend in background
Write-Host "[*] Starting Frontend (port 5173)..." -ForegroundColor Yellow
$frontendJob = Start-Job -ScriptBlock {
    Set-Location "$using:PWD\frontend"
    npm run dev
}
Write-Host "  Frontend started (Job ID: $($frontendJob.Id))" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Development servers started!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Backend:  http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "  Frontend: http://127.0.0.1:5173" -ForegroundColor Cyan
Write-Host "  API Docs: http://127.0.0.1:8000/api/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop all servers..." -ForegroundColor Gray
Write-Host ""

# Monitor jobs and show output
try {
    while ($true) {
        # Check if jobs are still running
        $backendState = (Get-Job -Id $backendJob.Id).State
        $frontendState = (Get-Job -Id $frontendJob.Id).State

        if ($backendState -eq "Failed" -or $frontendState -eq "Failed") {
            Write-Host "[ERROR] A server has stopped unexpectedly" -ForegroundColor Red
            Receive-Job -Id $backendJob.Id -ErrorAction SilentlyContinue
            Receive-Job -Id $frontendJob.Id -ErrorAction SilentlyContinue
            break
        }

        Start-Sleep -Seconds 2
    }
} finally {
    Write-Host ""
    Write-Host "[*] Stopping servers..." -ForegroundColor Yellow
    Stop-Job -Id $backendJob.Id -ErrorAction SilentlyContinue
    Stop-Job -Id $frontendJob.Id -ErrorAction SilentlyContinue
    Remove-Job -Id $backendJob.Id -Force -ErrorAction SilentlyContinue
    Remove-Job -Id $frontendJob.Id -Force -ErrorAction SilentlyContinue
    Write-Host "  Servers stopped." -ForegroundColor Green
}
