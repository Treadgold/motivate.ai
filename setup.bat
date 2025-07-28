@echo off
cls
echo.
echo ========================================
echo   Motivate.AI - Windows Setup
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "README.md" (
    echo ERROR: Please run this from the project root directory
    echo Make sure you can see README.md in the current folder
    pause
    exit /b 1
)

echo [1/5] Creating environment files...
echo.

REM Create backend .env file
if not exist "backend\.env" (
    if exist "shared\config.env.example" (
        copy "shared\config.env.example" "backend\.env" > nul
        echo   + Created backend\.env
    ) else (
        echo   ! shared\config.env.example not found - creating basic .env
        echo DATABASE_URL=sqlite:///./motivate_ai.db > "backend\.env"
        echo DEBUG=true >> "backend\.env"
    )
) else (
    echo   + backend\.env already exists
)

REM Create desktop .env file  
if not exist "desktop\.env" (
    if exist "shared\config.env.example" (
        copy "shared\config.env.example" "desktop\.env" > nul
        echo   + Created desktop\.env
    ) else (
        echo   ! shared\config.env.example not found - creating basic .env
        echo API_BASE_URL=http://127.0.0.1:8010/api/v1 > "desktop\.env"
        echo IDLE_THRESHOLD_MINUTES=10 >> "desktop\.env"
    )
) else (
    echo   + desktop\.env already exists
)

echo.
echo [2/5] Setting up Backend API...
echo.

cd backend
if exist "venv" (
    echo   + Virtual environment already exists
) else (
    echo   -> Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo   ERROR: Failed to create virtual environment
        echo   Make sure Python 3.9+ is installed and in your PATH
        cd ..
        pause
        exit /b 1
    )
    echo   + Virtual environment created
)

echo   -> Installing backend dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip > nul 2>&1
pip install -r requirements.txt
if errorlevel 1 (
    echo   ERROR: Failed to install backend dependencies
    echo   Check the error messages above
    cd ..
    pause
    exit /b 1
)
echo   + Backend dependencies installed
call deactivate
cd ..

echo.
echo [3/5] Setting up Desktop App...
echo.

cd desktop
if exist "venv" (
    echo   + Virtual environment already exists
) else (
    echo   -> Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo   ERROR: Failed to create virtual environment
        cd ..
        pause
        exit /b 1
    )
    echo   + Virtual environment created
)

echo   -> Installing desktop dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip > nul 2>&1
pip install -r requirements.txt
if errorlevel 1 (
    echo   ERROR: Failed to install desktop dependencies
    echo   Check the error messages above
    cd ..
    pause
    exit /b 1
)
echo   + Desktop dependencies installed
call deactivate
cd ..

echo.
echo [4/5] Testing installations...
echo.

REM Test Ollama availability
echo   -> Checking Ollama...
ollama list >nul 2>&1
if errorlevel 1 (
    echo   ! Ollama not found - AI features will use fallback suggestions
    echo     Install from: https://ollama.ai
) else (
    echo   + Ollama available
    echo   -> Checking for qwen3max model...
    ollama list | findstr "qwen3max" >nul 2>&1
    if errorlevel 1 (
        echo   ! qwen3max model not found
        echo     Install with: ollama pull qwen3max
    ) else (
        echo   + qwen3max model ready
    )
)

REM Quick test of backend
cd backend
call venv\Scripts\activate.bat
python -c "import fastapi; print('  + Backend ready')" 2>nul || echo "  ! Backend test failed"
call deactivate
cd ..

REM Quick test of desktop
cd desktop  
call venv\Scripts\activate.bat
python -c "import pystray; print('  + Desktop ready')" 2>nul || echo "  ! Desktop test failed"
call deactivate
cd ..

echo.
echo [5/5] Setup Complete!
echo.
echo ========================================
echo   Ready to start Motivate.AI
echo ========================================
echo.
echo Next steps:
echo.
echo 1. Start the Backend API:
echo    cd backend
echo    venv\Scripts\activate
echo    python main.py
echo.
echo 2. In a new terminal, start the Desktop App:
echo    cd desktop  
echo    venv\Scripts\activate
echo    python main.py
echo.
echo 3. Open your browser to:
echo    http://localhost:8010/docs
echo.
echo 4. For AI suggestions, make sure Ollama is running:
echo    ollama serve
echo.
echo The API docs will let you create your first project!
echo Smart suggestions need qwen3max model: ollama pull qwen3max
echo.
pause
