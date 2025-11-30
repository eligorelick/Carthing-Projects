@echo off
title Portfolio Tracker Server
color 0A
cls
echo.
echo  ========================================
echo   PORTFOLIO TRACKER SERVER
echo  ========================================
echo.
echo  This server fetches real-time stock data
echo  and displays your portfolio on Car Thing.
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

REM Check if yfinance is installed
python -c "import yfinance" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo  [INSTALLING] yfinance package...
    pip install yfinance --quiet --disable-pip-version-check
    if %ERRORLEVEL% NEQ 0 (
        color 0C
        echo.
        echo  [ERROR] Failed to install yfinance!
        echo  Please check your internet connection.
        echo.
        pause
        exit /b 1
    )
    echo  [OK] yfinance installed
    echo.
)

cd /d "%~dp0"

REM Show configuration info
echo  ========================================
echo   CONFIGURATION
echo  ========================================
echo.
echo  Server will start on: 172.16.42.1:8080
echo  Car Thing IP: 172.16.42.2
echo.
echo  DEMO DATA is loaded by default.
echo  To track YOUR portfolio:
echo   1. Edit portfolio_server.py
echo   2. Replace the HOLDINGS section
echo   3. Restart this server
echo.
echo  ========================================
echo.
echo  Starting server now...
echo  Press Ctrl+C to stop the server.
echo  ========================================
echo.

REM Start the server
python portfolio_server.py

REM Server stopped
color 0E
echo.
echo  ========================================
echo   Server stopped.
echo  ========================================
echo.
pause
