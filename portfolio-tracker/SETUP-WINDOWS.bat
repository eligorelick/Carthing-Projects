@echo off
setlocal enabledelayedexpansion
title Car Thing - Windows Setup
color 0B

cls
echo.
echo  ===============================================================
echo   CAR THING - WINDOWS SETUP
echo  ===============================================================
echo.
echo   This will check your system and install dependencies.
echo.
echo  ===============================================================
echo.
pause

REM ============================================================================
REM  STEP 1: Check Python
REM ============================================================================

cls
echo.
echo  ===============================================================
echo   STEP 1 of 3: Checking Python
echo  ===============================================================
echo.

python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo   [X] Python is NOT installed!
    echo.
    echo   Please install Python 3.8+ from:
    echo   https://www.python.org/downloads/
    echo.
    echo   Make sure to check "Add Python to PATH" during install.
    echo.
    pause
    exit /b 1
)

color 0A
echo   [OK] Python is installed
echo.
pause

REM ============================================================================
REM  STEP 2: Check OpenSSH
REM ============================================================================

cls
echo.
echo  ===============================================================
echo   STEP 2 of 3: Checking OpenSSH
echo  ===============================================================
echo.

where ssh >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    color 0E
    echo   [!] OpenSSH is not installed
    echo.
    echo   To deploy to Car Thing, you need OpenSSH.
    echo.
    echo   INSTALL IT:
    echo   1. Open Windows Settings
    echo   2. Go to: Apps ^> Optional Features
    echo   3. Click "Add a feature"
    echo   4. Find and install "OpenSSH Client"
    echo   5. Restart this script
    echo.
    echo   (Alternatively, you can skip this and install it later)
    echo.
    pause
) else (
    color 0A
    echo   [OK] OpenSSH is installed
    echo.
    pause
)

REM ============================================================================
REM  STEP 3: Install Dependencies
REM ============================================================================

cls
echo.
echo  ===============================================================
echo   STEP 3 of 3: Installing Python Dependencies
echo  ===============================================================
echo.

echo   Installing required packages...
echo.

pip install yfinance --quiet --disable-pip-version-check 2>nul
if %ERRORLEVEL% EQU 0 (
    echo   [OK] yfinance installed
) else (
    echo   [!] yfinance installation failed
)

echo.
echo   Installation complete!
echo.
pause

REM ============================================================================
REM  SETUP COMPLETE
REM ============================================================================

cls
color 0A
echo.
echo  ===============================================================
echo   SETUP COMPLETE!
echo  ===============================================================
echo.
echo   Your system is ready.
echo.
echo   NEXT STEPS:
echo.
echo   1. Read README.md in this folder for setup instructions
echo.
echo   2. To start the server:
echo      - Double-click START-SERVER.bat
echo      - Keep the window open
echo.
echo   3. To deploy to Car Thing:
echo      - Make sure server is running
echo      - Double-click DEPLOY.bat
echo.
echo   For detailed instructions, see README.md
echo.
echo  ===============================================================
echo.
pause
