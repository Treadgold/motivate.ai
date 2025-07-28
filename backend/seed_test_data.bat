@echo off
echo.
echo ========================================
echo   Motivate.AI Test Data Seeding
echo ========================================
echo.
echo This will replace all current data with fresh test data.
echo Press Ctrl+C to cancel, or
pause
echo.

cd /d "%~dp0"
python seed_data.py

echo.
echo Press any key to continue...
pause > nul 