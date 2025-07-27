@echo off
echo.
echo ========================================
echo   Testing Motivate.AI System
echo ========================================
echo.

REM Test 1: Backend API
echo [1/4] Testing Backend API...
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo   X Backend API not responding
    echo      Make sure backend is running: start_backend.bat
) else (
    echo   + Backend API responding
)

echo.
echo [2/4] Testing AI Service...
curl -s http://localhost:8000/api/v1/ai/health >nul 2>&1
if errorlevel 1 (
    echo   X AI service not responding
) else (
    echo   + AI service responding
    echo      Checking Ollama connection...
    curl -s "http://localhost:8000/api/v1/ai/health" | findstr "true" >nul 2>&1
    if errorlevel 1 (
        echo      ! Ollama not connected (will use fallback suggestions)
    ) else (
        echo      + Ollama connected with qwen3max
    )
)

echo.
echo [3/4] Testing Project Creation...
curl -s -X POST "http://localhost:8000/api/v1/projects" ^
     -H "Content-Type: application/json" ^
     -d "{\"title\":\"Test Workshop Project\",\"description\":\"Organize my workshop tools\",\"location\":\"garage\"}" >nul 2>&1
if errorlevel 1 (
    echo   X Cannot create projects
) else (
    echo   + Project creation working
)

echo.
echo [4/4] Testing AI Suggestions...
curl -s "http://localhost:8000/api/v1/suggestions/quick" | findstr "title" >nul 2>&1
if errorlevel 1 (
    echo   X Suggestions not working
) else (
    echo   + AI suggestions working
)

echo.
echo ========================================
echo   Test Complete
echo ========================================
echo.
echo Open http://localhost:8000/docs to explore the API
echo.
pause 
