@echo off
title NIFTY 50 Quantitative Visualizer Terminal
color 0A
echo ===================================================================
echo     NIFTY 50 3-Year Quantitative Visualizer Terminal Launcher
echo     Dow Theory Market Structure, Williams %%R, BRC Engine, RSI
echo ===================================================================
echo.

cd /d "%~dp0"

echo [1/3] Checking dataset preprocessor...
if not exist "nifty_3yr_data.json" (
    echo Preprocessing 3-year multi-timeframe datasets...
    "C:\Users\kolab\AppData\Local\Programs\Python\Python313\python.exe" engine.py
)

echo [2/3] Launching local high-performance HTTP & API server on port 8888...
start "NiftyVisualizerServer" "C:\Users\kolab\AppData\Local\Programs\Python\Python313\python.exe" server.py

echo [3/3] Opening NIFTY 50 Visualizer Terminal in default browser...
timeout /t 2 /nobreak >nul
start http://localhost:8888

echo.
echo ===================================================================
echo   Visualizer Terminal is actively running at http://localhost:8888
echo   To terminate the server, close the NiftyVisualizerServer window.
echo ===================================================================
pause
