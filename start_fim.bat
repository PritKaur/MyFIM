@echo off
echo Starting MyFIM...

python baseline.py
if %ERRORLEVEL% NEQ 0 (
    echo Baseline creation was cancelled or failed. Closing MyFIM.
    timeout /t 3 >nul
    exit /b 1
)

start python dashboard.py
python monitor.py
pause