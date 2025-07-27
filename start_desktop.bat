@echo off
echo Starting Motivate.AI Desktop App...
echo.

if not exist "desktop\venv\Scripts\activate.bat" (
    echo ERROR: Desktop app not set up yet
    echo Please run setup.bat first
    pause
    exit /b 1
)

echo Make sure the backend is running first!
echo Backend should be at: http://localhost:8000
echo.
echo The desktop app will run in the system tray.
echo Look for the icon in the bottom-right corner.
echo Press Ctrl+C to stop
echo.

cd desktop
call venv\Scripts\activate.bat
python main.py 