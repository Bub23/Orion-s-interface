@echo off
setlocal
set "ORION_ROOT=C:\Users\outla\OneDrive\OIRONSINTERFACE.worktrees\agents-orion-content-engine-v1"
cd /d "%ORION_ROOT%"

echo.
echo ORION INTERFACE STARTUP
echo Repo: %ORION_ROOT%
echo.

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set "PYTHON_CMD=python"
) else (
    where py >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        set "PYTHON_CMD=py"
    ) else (
        echo FAIL: Python was not found on PATH.
        pause
        exit /b 1
    )
)

%PYTHON_CMD% startup_preflight.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Orion preflight failed. Fix the FAIL items above.
    pause
    exit /b 1
)

echo.
echo Starting Orion Flask server in a separate window...
echo.
start "Orion Flask Server" %PYTHON_CMD% web_app.py

echo Waiting for Flask to come online...
timeout /t 5 /nobreak >nul

%PYTHON_CMD% route_smoke_test.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Orion started, but route smoke test failed. Check the Flask server window.
    pause
    exit /b 1
)

echo.
echo ORION STARTUP PASS
echo Dashboard: http://localhost:8000
start "" "http://localhost:8000"

echo.
echo Orion is running in the Flask server window.
echo Close that window to stop Orion.
pause
