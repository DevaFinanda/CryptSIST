@echo off
title CryptSIST Real-Time MT5 Integration Launcher
color 0A

echo.
echo ============================================================
echo    🚀 CryptSIST Real-Time MT5 Integration Launcher v3.0
echo ============================================================
echo.
echo 📊 Starting CryptSIST Real-Time Analysis System...
echo.

REM Change to the script directory
cd /d "E:\Kecerdasan Buatan\UAS\CryptoAgents"

echo 🔍 Checking Python environment...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

echo.
echo 📡 Starting CryptSIST MT5 Server...
echo 🌐 Server will be available at: http://localhost:8000
echo 🎯 Real-time analysis endpoints ready
echo.

REM Start the MT5 server in background
start "CryptSIST MT5 Server" /min cmd /c "python mt5_server.py"

echo ⏳ Waiting for server to start...
timeout /t 3 /nobreak > nul

echo.
echo 🌉 Starting MT5 Bridge...
echo 📊 Bridge will handle real-time signal transmission
echo.

REM Start the MT5 bridge
start "CryptSIST MT5 Bridge" cmd /c "python mt5_integration/bridge/mt5_bridge.py"

echo.
echo ✅ CryptSIST Real-Time System Started Successfully!
echo.
echo 📋 Next Steps:
echo ├── 1. Open MetaTrader 5
echo ├── 2. Compile: CryptSIST_RealTime_Pro.mq5 (Expert)
echo ├── 3. Compile: CryptSIST_RealTime_Indicator.mq5 (Indicator)
echo ├── 4. Attach EA to BTCUSD chart
echo ├── 5. Attach Indicator to chart
echo └── 6. Enable Auto Trading (green button)
echo.
echo 🔧 Configuration:
echo ├── Server URL: http://localhost:8000
echo ├── Analysis Interval: 500ms (real-time)
echo ├── Enable Auto Trading: Set to 'true' for live trading
echo └── Lot Size: Start with 0.01 for testing
echo.
echo 📊 Features Active:
echo ├── ⚡ Real-time signal analysis (500ms interval)
echo ├── 🎯 BUY/SELL/HOLD signals with confidence
echo ├── 📈 Live dashboard on chart
echo ├── 🛡️ Advanced risk management
echo ├── 📱 Sound alerts and notifications
echo └── 📊 Performance tracking
echo.
echo 🌐 Server Endpoints:
echo ├── Health: http://localhost:8000/health
echo ├── BTC Signal: http://localhost:8000/signal/BTCUSD
echo ├── ETH Signal: http://localhost:8000/signal/ETHUSD
echo └── Any Symbol: http://localhost:8000/signal/[SYMBOL]
echo.
echo 💡 Tips:
echo ├── Start with demo account for testing
echo ├── Use small lot sizes initially (0.01)
echo ├── Monitor the live dashboard for real-time updates
echo ├── Check confidence levels before manual trades
echo └── Review daily performance statistics
echo.
echo ⚠️  Important Notes:
echo ├── Enable WebRequest in MT5: Tools ^> Options ^> Expert Advisors
echo ├── Add URL to allowed list: http://localhost:8000
echo ├── Ensure Auto Trading is enabled (green button)
echo └── Keep this window open while trading
echo.

REM Keep window open
echo 🔄 System running... Press any key to stop all services
pause > nul

echo.
echo 🛑 Stopping CryptSIST services...
taskkill /f /im python.exe /fi "WINDOWTITLE eq CryptSIST MT5 Server" > nul 2>&1
taskkill /f /im cmd.exe /fi "WINDOWTITLE eq CryptSIST MT5 Bridge" > nul 2>&1

echo ✅ All services stopped!
echo 👋 Thank you for using CryptSIST Real-Time MT5 Integration!
pause
