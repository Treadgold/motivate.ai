@echo off
cls
echo.
echo ========================================
echo   Motivate.AI - Development Startup
echo ========================================
echo.

REM Check if setup was completed
if not exist "backend\venv\Scripts\activate.bat" (
    echo ERROR: Setup not completed yet
    echo Please run setup.bat first
    pause
    exit /b 1
)

REM Check if we're already running (avoid conflicts)
echo [1/5] Checking for existing instances...
tasklist /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq *Motivate.AI*" 2>NUL | find /I /N "python.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo   ! Found existing Motivate.AI processes
    echo   -> Stopping existing instances...
    taskkill /F /FI "WINDOWTITLE eq *Motivate.AI*" >nul 2>&1
    timeout /t 2 /nobreak >nul
)
echo   + No conflicts detected

echo.
echo [2/5] Starting AI Service (Ollama)...
tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I /N "ollama.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo   + Ollama already running
) else (
    echo   -> Starting Ollama server...
    start /B ollama serve
    echo   + Ollama server started
    timeout /t 3 /nobreak >nul
)

REM Check for qwen3max model
echo   -> Verifying AI model...
ollama list | findstr "qwen3max" >nul 2>&1
if errorlevel 1 (
    echo   ! qwen3max model not found
    echo   -> Would you like to download it now? (This takes several minutes)
    choice /C YN /N /M "Download qwen3max model? (Y/N): "
    if errorlevel 2 (
        echo   -> Skipping model download. AI will use fallback suggestions.
    ) else (
        echo   -> Downloading qwen3max model...
        ollama pull qwen3max
        echo   + Model downloaded successfully
    )
) else (
    echo   + qwen3max model ready
)

echo.
echo [3/5] Starting Backend API...
cd backend
call venv\Scripts\activate.bat

echo   -> Checking backend dependencies...
python -c "import fastapi, uvicorn, sqlalchemy" 2>nul
if errorlevel 1 (
    echo   ! Backend dependencies missing
    echo   -> Installing dependencies...
    pip install -r requirements.txt >nul 2>&1
    echo   + Dependencies installed
) else (
    echo   + Backend dependencies verified
)

echo   -> Starting backend server...
start "Motivate.AI Backend" cmd /k "echo Starting Backend API on http://localhost:8010 && python main.py"
call deactivate
cd ..

REM Wait for backend to start
echo   -> Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

REM Health check with retry
set "BACKEND_READY=0"
for /L %%i in (1,1,5) do (
    curl -s http://localhost:8010/health >nul 2>&1
    if not errorlevel 1 (
        set "BACKEND_READY=1"
        goto backend_ready
    )
    echo   -> Attempt %%i/5: Backend still starting...
    timeout /t 2 /nobreak >nul
)

:backend_ready
if "%BACKEND_READY%"=="1" (
    echo   + Backend API ready at http://localhost:8010
) else (
    echo   ! Backend failed to start properly
    echo   -> Check the Backend window for errors
)

echo.
echo [4/5] Starting Desktop App...
cd desktop
call venv\Scripts\activate.bat

echo   -> Checking desktop dependencies...
python -c "import pystray, PIL, psutil" 2>nul
if errorlevel 1 (
    echo   ! Desktop dependencies missing
    echo   -> Installing dependencies...
    pip install -r requirements.txt >nul 2>&1
    echo   + Dependencies installed
) else (
    echo   + Desktop dependencies verified
)

echo   -> Starting desktop application...
start "Motivate.AI Desktop" cmd /k "echo Starting Desktop App && python main.py"
call deactivate
cd ..

echo.
echo [5/5] Development Environment Ready!
echo.
echo ========================================
echo   🚀 Motivate.AI Development Mode
echo ========================================
echo.
echo Services Status:
if "%BACKEND_READY%"=="1" (
    echo  [OK] Backend API: http://localhost:8010
    echo  [OK] API Docs: http://localhost:8010/docs
) else (
    echo  [ERR] Backend API: Failed to start
)
echo  [OK] Desktop App: Running in system tray
echo  [OK] AI Service: Ollama running

echo.
echo Development Commands:
echo  - View API Documentation: http://localhost:8010/docs
echo  - Run Tests: run_tests.bat
echo  - View Logs: Check the terminal windows
echo  - Stop All: Press Ctrl+C in each window
echo.

REM Open API docs automatically
choice /C YN /N /M "Open API docs in browser? (Y/N): "
if not errorlevel 2 (
    start http://localhost:8010/docs
)

echo.
echo Press any key to exit this window (services will keep running)...
pause >nul 