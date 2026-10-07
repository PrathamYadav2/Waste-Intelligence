@echo off
REM ==============================================================================
REM One-Click Launcher for AI Waste Intelligence System
REM ==============================================================================

title AI Waste Recovery & Regional Decision Intelligence

cd /d "%~dp0"
set PYTHONPATH=.

echo ======================================================================
echo  Starting AI Waste Recovery & Decision Intelligence System
echo ======================================================================
echo.

REM Automatically open Chrome / Default Browser after 2 seconds
start "" http://127.0.0.1:8000/

REM Check Python executable
if exist "C:\Program Files\Python312\python.exe" (
    echo Using Python at: C:\Program Files\Python312\python.exe
    "C:\Program Files\Python312\python.exe" app.py
) else (
    python app.py
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Server encountered an error. Check above messages.
    pause
)
