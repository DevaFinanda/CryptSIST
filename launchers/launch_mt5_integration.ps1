# CryptSIST-MT5 Integration Launcher (PowerShell)

Write-Host "🔷 CryptSIST-MT5 Integration Launcher" -ForegroundColor Cyan
Write-Host "🔷 Checking dependencies..." -ForegroundColor Cyan

# Check if Python is installed
try {
    $pythonVersion = python --version 2>$null
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ and try again" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if MT5 package is installed
try {
    python -c "import MetaTrader5" 2>$null
    Write-Host "✅ MetaTrader5 package found" -ForegroundColor Green
} catch {
    Write-Host "⚠️  MetaTrader5 package not found" -ForegroundColor Yellow
    Write-Host "Installing required packages..." -ForegroundColor Yellow
    
    try {
        pip install -r mt5_integration\requirements.txt
        Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host "🚀 Starting CryptSIST-MT5 Integration..." -ForegroundColor Green
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot

# Run the integration
try {
    python mt5_integration\run_integration.py
} catch {
    Write-Host "❌ Error running integration: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "👋 Integration stopped" -ForegroundColor Cyan
Read-Host "Press Enter to exit"
