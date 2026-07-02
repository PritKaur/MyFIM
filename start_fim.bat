@echo off
echo Starting MyFIM...

start /min "MyFIM Dashboard" cmd /c python dashboard.py
timeout /t 2 >nul

start http://localhost:5000/login

python baseline.py
if %ERRORLEVEL% NEQ 0 (
    echo Baseline creation was cancelled or failed. Closing MyFIM.
    taskkill /FI "WINDOWTITLE eq MyFIM Dashboard*" /T /F >nul 2>&1
    timeout /t 3 >nul
    exit /b 1
)

start python monitor.py
pause