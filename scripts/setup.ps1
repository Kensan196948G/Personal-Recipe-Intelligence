# Personal Recipe Intelligence - Setup Script (Windows PowerShell)
# Usage: .\scripts\setup.ps1

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Personal Recipe Intelligence" -ForegroundColor Cyan
Write-Host "  Environment Setup (Windows)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "[1/5] Checking Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Python not found. Please install Python 3.11+" -ForegroundColor Red
    exit 1
}
Write-Host "  Found: $pythonVersion" -ForegroundColor Green

# Check Node.js
Write-Host "[2/5] Checking Node.js..." -ForegroundColor Yellow
$nodeVersion = node --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Node.js not found. Please install Node.js 20+" -ForegroundColor Red
    exit 1
}
Write-Host "  Found: Node.js $nodeVersion" -ForegroundColor Green

# Create virtual environment
Write-Host "[3/5] Setting up Python virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path ".venv")) {
    python -m venv .venv
    Write-Host "  Created .venv directory" -ForegroundColor Green
} else {
    Write-Host "  .venv already exists" -ForegroundColor Gray
}

# Activate venv and install dependencies
Write-Host "[4/5] Installing Python dependencies..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt --quiet
Write-Host "  Python dependencies installed" -ForegroundColor Green

# Install frontend dependencies
Write-Host "[5/5] Installing frontend dependencies..." -ForegroundColor Yellow
Push-Location frontend
npm install --silent
Pop-Location
Write-Host "  Frontend dependencies installed" -ForegroundColor Green

# Create directories
Write-Host ""
Write-Host "[*] Creating required directories..." -ForegroundColor Yellow
$dirs = @("data", "data/db", "data/images", "data/backups", "logs")
foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  Created: $dir" -ForegroundColor Gray
    }
}

# Create .env if not exists
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "  Created .env from .env.example" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Edit .env file with your API keys"
Write-Host "  2. Run: .\scripts\dev.ps1"
Write-Host ""
