@echo off
echo Starting MyFIM...
python baseline.py
start python dashboard.py
python monitor.py
pause