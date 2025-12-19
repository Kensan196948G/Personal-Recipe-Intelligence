# Personal Recipe Intelligence - Test Runner (Windows PowerShell)
# Usage: .\scripts\test.ps1 [options]
#
# Options:
#   -backend   : Run backend tests only
#   -frontend  : Run frontend tests only
#   -e2e       : Run E2E tests only
#   -coverage  : Generate coverage report

param(
    [switch]$backend,
    [switch]$frontend,
    [switch]$e2e,
    [switch]$coverage
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Personal Recipe Intelligence" -ForegroundColor Cyan
Write-Host "  Test Runner (Windows)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment if exists
if (Test-Path ".venv\Scripts\Activate.ps1") {
    & .\.venv\Scripts\Activate.ps1
}

$runAll = -not ($backend -or $frontend -or $e2e)
$exitCode = 0

# Backend tests
if ($backend -or $runAll) {
    Write-Host "[Backend Tests]" -ForegroundColor Yellow
    Write-Host "Running pytest..." -ForegroundColor Gray

    if ($coverage) {
        python -m pytest backend/tests/ --cov=backend --cov-report=html --cov-report=term -v
    } else {
        python -m pytest backend/tests/ -v
    }

    if ($LASTEXITCODE -ne 0) {
        Write-Host "  Backend tests: FAILED" -ForegroundColor Red
        $exitCode = 1
    } else {
        Write-Host "  Backend tests: PASSED" -ForegroundColor Green
    }
    Write-Host ""
}

# Frontend tests
if ($frontend -or $runAll) {
    Write-Host "[Frontend Tests]" -ForegroundColor Yellow
    Write-Host "Running bun test..." -ForegroundColor Gray

    Push-Location frontend

    # Try bun first, fallback to npm
    $bunExists = Get-Command bun -ErrorAction SilentlyContinue
    if ($bunExists) {
        bun test
    } else {
        npm test
    }

    if ($LASTEXITCODE -ne 0) {
        Write-Host "  Frontend tests: FAILED" -ForegroundColor Red
        $exitCode = 1
    } else {
        Write-Host "  Frontend tests: PASSED" -ForegroundColor Green
    }

    Pop-Location
    Write-Host ""
}

# E2E tests
if ($e2e -or $runAll) {
    Write-Host "[E2E Tests]" -ForegroundColor Yellow
    Write-Host "Running Playwright..." -ForegroundColor Gray

    npx playwright test

    if ($LASTEXITCODE -ne 0) {
        Write-Host "  E2E tests: FAILED" -ForegroundColor Red
        $exitCode = 1
    } else {
        Write-Host "  E2E tests: PASSED" -ForegroundColor Green
    }
    Write-Host ""
}

# Summary
Write-Host "========================================" -ForegroundColor Cyan
if ($exitCode -eq 0) {
    Write-Host "  All tests PASSED!" -ForegroundColor Green
} else {
    Write-Host "  Some tests FAILED" -ForegroundColor Red
}
Write-Host "========================================" -ForegroundColor Cyan

if ($coverage) {
    Write-Host ""
    Write-Host "Coverage report: htmlcov/index.html" -ForegroundColor Gray
}

exit $exitCode
