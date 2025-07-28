@echo off
echo.
echo ========================================
echo   Starting Complete Motivate.AI System
echo ========================================
echo.

REM Check if setup was completed
if not exist "backend\venv\Scripts\activate.bat" (
    echo ERROR: Setup not completed yet
    echo Please run setup.bat first
    pause
    exit /b 1
)

echo [1/3] Starting Ollama...
echo.

REM Check if Ollama is already running
tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I /N "ollama.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo   + Ollama already running
) else (
    echo   -> Starting Ollama server...
    start /B ollama serve
    echo   + Ollama server started
    timeout /t 3 /nobreak >nul
)

echo   -> Checking qwen3max model...
ollama list | findstr "qwen3max" >nul 2>&1
if errorlevel 1 (
    echo   -> Downloading qwen3max model (this may take a while)...
    ollama pull qwen3max
) else (
    echo   + qwen3max model ready
)

echo.
echo [2/3] Starting Backend API...
echo.
start "Motivate.AI Backend" /MIN cmd /c "cd backend && call venv\Scripts\activate.bat && python main.py"
echo   + Backend starting (minimized window)
timeout /t 3 /nobreak >nul

echo.
echo [3/3] Starting Desktop App...
echo.
start "Motivate.AI Desktop" /MIN cmd /c "cd desktop && call venv\Scripts\activate.bat && python main.py"
echo   + Desktop app starting (minimized window)

echo.
echo ========================================
echo   All systems running!
echo ========================================
echo.
echo  Backend API: http://localhost:8010/docs
echo  Desktop app: Running in system tray
echo  AI: qwen3max via Ollama
echo.
echo Check minimized windows if any errors occur.
echo Press any key to open the API docs...
pause >nul

start http://localhost:8010/docs 
