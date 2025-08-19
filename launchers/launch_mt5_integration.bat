@echo off
echo ================================================================
echo 🔷 CryptSIST-MT5 Integration Launcher  
echo 🔷 Demo Account: Deva FS (95426869)
echo 🔷 Server: MetaQuotes-Demo
echo ================================================================
echo.

echo 🔍 Checking system requirements...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo 💡 Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if MT5 package is installed
python -c "import MetaTrader5" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  MetaTrader5 package not found
    echo Installing required packages...
    pip install -r mt5_integration\requirements.txt
    if errorlevel 1 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
)

echo ✅ Dependencies OK
echo 🚀 Starting CryptSIST-MT5 Integration...
echo.

REM Change to the correct directory
cd /d "%~dp0"

REM Run the integration
cd mt5_integration
python main.py

echo.
echo 👋 Integration stopped
pause
