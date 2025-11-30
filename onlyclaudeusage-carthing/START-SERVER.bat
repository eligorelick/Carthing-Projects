@echo off
title Claude Usage Server for Car Thing
color 0A
echo.
echo  ========================================
echo   CLAUDE USAGE SERVER FOR CAR THING
echo  ========================================
echo.
echo  Starting server...
echo  Keep this window open while using the display.
echo.
echo  Press Ctrl+C to stop the server.
echo  ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo  ERROR: Python is not installed!
    echo  Please install Python from python.org
    echo.
    pause
    exit /b 1
)

REM Check if Flask is installed
python -c "import flask" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo  Installing Flask...
    pip install flask
    echo.
)

REM Check if curl_cffi is installed
python -c "import curl_cffi" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo  Installing curl_cffi...
    pip install curl_cffi
    echo.
)

cd /d "%~dp0"

REM Start the server
python claude_usage_server.py
echo.
echo  Server stopped.
pause
