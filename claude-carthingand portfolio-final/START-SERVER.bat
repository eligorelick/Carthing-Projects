@echo off
title Car Thing Dashboard Server
color 0A
cls
echo.
echo  ========================================
echo   CAR THING DASHBOARD SERVER
echo   Claude Usage + Portfolio + 2048 Game
echo  ========================================
echo.
echo  This all-in-one server provides:
echo   - Claude API usage monitoring
echo   - Real-time stock portfolio tracking
echo   - 2048 game for entertainment
echo.
echo  Keep this window open while using!
echo  ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo  [ERROR] Python is not installed!
    echo.
    echo  Please run SETUP-WINDOWS.bat in the main folder
    echo  or install Python from python.org
    echo.
    pause
    exit /b 1
)

echo  [OK] Python is installed
echo.

REM Check and install dependencies
echo  Checking dependencies...
echo.

python -c "import flask" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo  [INSTALLING] Flask...
    pip install flask --quiet --disable-pip-version-check
)

python -c "import curl_cffi" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo  [INSTALLING] curl_cffi...
    pip install curl_cffi --quiet --disable-pip-version-check
)

python -c "import yfinance" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo  [INSTALLING] yfinance...
    pip install yfinance --quiet --disable-pip-version-check
)

echo  [OK] All dependencies installed
echo.

cd /d "%~dp0"

REM Show configuration info
echo  ========================================
echo   CONFIGURATION
echo  ========================================
echo.
echo  Server will start on: 172.16.42.1:8080
echo  Car Thing IP: 172.16.42.2
echo.
echo  BEFORE FIRST USE:
echo   1. Edit carthing_server.py
echo   2. Add your Claude ORG_ID and SESSION_KEY
echo   3. (Portfolio has DEMO DATA by default)
echo.
echo  Portfolio demo includes:
echo   - 3 shares AAPL @ $120
echo   - 2 shares SPY @ $450
echo   - 5 shares MSFT @ $375
echo   - 10 shares VTI @ $220
echo.
echo  ========================================
echo.
echo  Starting server now...
echo  Press Ctrl+C to stop the server.
echo  ========================================
echo.

REM Start the server
python carthing_server.py

REM Server stopped
color 0E
echo.
echo  ========================================
echo   Server stopped.
echo  ========================================
echo.
pause
