@echo off
setlocal enabledelayedexpansion
title Deploy Claude Usage Display to Car Thing
color 0B
cls
echo.
echo  ========================================
echo   DEPLOY CLAUDE USAGE TO CAR THING
echo  ========================================
echo.
echo  This will deploy the Claude usage
echo  monitor display to your Car Thing.
echo.
echo  Make sure START-SERVER.bat is running!
echo  ========================================
echo.

set CARTHING_IP=172.16.42.2

REM Check if SSH is available
where ssh >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo  [ERROR] SSH is not installed!
    echo.
    echo  Please run SETUP-WINDOWS.bat in the main folder
    echo  to install OpenSSH.
    echo.
    pause
    exit /b 1
)

REM Test connection to Car Thing
echo  Testing connection to Car Thing...
ping -n 1 -w 1000 %CARTHING_IP% >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    color 0E
    echo.
    echo  [WARNING] Cannot ping Car Thing at %CARTHING_IP%
    echo.
    echo  This might be normal, attempting deployment anyway...
    echo.
    timeout /t 2 >nul
)

echo  [1/4] Remounting filesystem as read-write...
ssh -o StrictHostKeyChecking=no root@%CARTHING_IP% "mount -o remount,rw /" 2>nul

echo  [2/4] Copying display file to Car Thing...
scp -o StrictHostKeyChecking=no "%~dp0claude-usage-display.html" root@%CARTHING_IP%:/opt/custom/claude-usage-display.html 2>nul
set SCP_RESULT=%ERRORLEVEL%

if !SCP_RESULT! EQU 0 (
    color 0A
    echo  [OK] File copied successfully
    echo.
    echo  [3/4] Updating Chromium configuration...
    ssh -o StrictHostKeyChecking=no root@%CARTHING_IP% "sed -i 's|/opt/custom/[a-zA-Z0-9_-]*\.html|/opt/custom/claude-usage-display.html|g' /etc/sv/chromium/run" 2>nul
    echo  [OK] Configuration updated
    echo.
    echo  [4/4] Restarting Chromium on Car Thing...
    ssh -o StrictHostKeyChecking=no root@%CARTHING_IP% "sv restart chromium" 2>nul
    echo  [OK] Chromium restarted
    echo.
    echo  ========================================
    echo   SUCCESS! Deployment Complete
    echo  ========================================
    echo.
    echo  Your Car Thing should now display the
    echo  Claude usage monitor within a few seconds.
    echo.
    echo  If you don't see it:
    echo   1. Make sure START-SERVER.bat is running
    echo   2. Check server is on 172.16.42.1:8080
    echo   3. Try running DEPLOY.bat again
    echo.
    echo  ========================================
) else (
    color 0C
    echo.
    echo  ========================================
    echo   ERROR: Deployment Failed
    echo  ========================================
    echo.
    echo  Could not connect to Car Thing.
    echo.
    echo  TROUBLESHOOTING:
    echo.
    echo   1. Is Car Thing connected via USB?
    echo      - Check the USB cable is plugged in
    echo.
    echo   2. Is Car Thing powered on with Nocturne?
    echo      - You should see the Nocturne interface
    echo.
    echo   3. Is USB networking configured?
    echo      - Run: ping 172.16.42.2
    echo      - If it fails, run SETUP-WINDOWS.bat
    echo.
    echo   4. Have you set up SSH on Car Thing?
    echo      - See README.md in this folder for instructions
    echo      - You need to create /opt/custom/ folder
    echo.
    echo  ========================================
)

:end
echo.
echo  Press any key to close...
pause >nul
