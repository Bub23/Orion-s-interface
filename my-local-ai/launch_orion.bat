@echo off
REM Orion OS Launcher - Runs in background

cd /d "C:\Users\outla\Documents\Orion's interface\my-local-ai"

set ORION_LLM_TIMEOUT=12

REM Start Flask in background
start /B python app.py

REM Open browser after 3 seconds
timeout /t 3 /nobreak
start http://localhost:5000

pause
