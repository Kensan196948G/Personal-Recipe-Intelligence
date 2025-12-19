# E2E Test Runner (Windows PowerShell)
# Usage: .\scripts\test-e2e.ps1 [options]
#
# Options:
#   -ui       : Run in UI mode (interactive)
#   -debug    : Run in debug mode
#   -headed   : Run with browser visible
#   -report   : Open HTML report after test

param(
    [switch]$ui,
    [switch]$debug,
    [switch]$headed,
    [switch]$report,
    [string]$filter = ""
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Personal Recipe Intelligence" -ForegroundColor Cyan
Write-Host "  E2E Test Runner" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Playwright is installed
if (-not (Test-Path "node_modules/@playwright/test")) {
    Write-Host "[!] Playwright not found. Installing..." -ForegroundColor Yellow
    npm install -D @playwright/test
    npx playwright install chromium
}

# Build command
$cmd = "npx playwright test"

if ($ui) {
    $cmd += " --ui"
    Write-Host "[*] Running in UI mode..." -ForegroundColor Green
}
elseif ($debug) {
    $cmd += " --debug"
    Write-Host "[*] Running in debug mode..." -ForegroundColor Green
}
else {
    if ($headed) {
        $cmd += " --headed"
    }
    Write-Host "[*] Running automated tests..." -ForegroundColor Green
}

if ($filter -ne "") {
    $cmd += " --grep `"$filter`""
    Write-Host "[*] Filter: $filter" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[>] Executing: $cmd" -ForegroundColor Gray
Write-Host ""

# Run tests
Invoke-Expression $cmd
$exitCode = $LASTEXITCODE

Write-Host ""

if ($exitCode -eq 0) {
    Write-Host "[OK] All tests passed!" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Some tests failed (exit code: $exitCode)" -ForegroundColor Red
}

# Open report if requested
if ($report -or ($exitCode -ne 0)) {
    Write-Host ""
    Write-Host "[*] Opening test report..." -ForegroundColor Cyan
    npx playwright show-report tests/e2e/reports
}

exit $exitCode
