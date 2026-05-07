@echo off
REM Orion OS - Windows Startup Launcher
REM Copy this to: C:\Users\outla\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\

cd /d "C:\Users\outla\Documents\Orion's interface\my-local-ai"

set ORION_LLM_TIMEOUT=12

REM Run Flask silently in background
start /B "" python app.py

REM Wait for server to start
timeout /t 4 /nobreak >nul

REM Open browser
start http://localhost:5000

REM Exit this batch file
exit
