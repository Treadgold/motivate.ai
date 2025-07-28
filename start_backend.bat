@echo off
echo Starting Motivate.AI Backend...
echo.

if not exist "backend\venv\Scripts\activate.bat" (
    echo ERROR: Backend not set up yet
    echo Please run setup.bat first
    pause
    exit /b 1
)

cd backend
call venv\Scripts\activate.bat
echo Backend API starting at http://localhost:8010
echo Press Ctrl+C to stop
echo.
python main.py 