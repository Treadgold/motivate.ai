@echo off
cls
echo.
echo ========================================
echo   Motivate.AI - Test Suite Runner
echo ========================================
echo.

REM Check if setup was completed
if not exist "backend\venv\Scripts\activate.bat" (
    echo ERROR: Setup not completed yet
    echo Please run setup.bat first
    pause
    exit /b 1
)

set "FAILED_TESTS=0"

echo [1/4] Testing Backend API...
echo.

cd backend
call venv\Scripts\activate.bat

echo   -> Installing test dependencies (if needed)...
pip install pytest pytest-asyncio pytest-cov httpx > nul 2>&1

echo   ^-^> Running backend unit tests with coverage...
pytest tests/test_simple.py tests/test_integration_simple.py -v --cov=. --cov-report=term --cov-report=html:coverage_backend
if errorlevel 1 (
    echo   X Backend tests failed
    set /a FAILED_TESTS+=1
) else (
    echo   + Backend tests passed
)

call deactivate
cd ..

echo.
echo [2/4] Testing Desktop App...
echo.

cd desktop
call venv\Scripts\activate.bat

echo   -> Installing test dependencies (if needed)...
pip install pytest pytest-cov > nul 2>&1

echo   -> Running desktop unit tests with coverage...
pytest tests/ -v --cov=. --cov-report=term --cov-report=html:coverage_desktop
if errorlevel 1 (
    echo   X Desktop tests failed
    set /a FAILED_TESTS+=1
) else (
    echo   + Desktop tests passed
)

call deactivate
cd ..

echo.
echo [3/4] Testing API Integration...
echo.

echo   -> Checking if backend is running...
curl -s http://localhost:8010/health >nul 2>&1
if errorlevel 1 (
    echo   ! Backend not running - starting temporary instance...
    cd backend
    call venv\Scripts\activate.bat
    start "Test Backend" /MIN cmd /c "python main.py"
    call deactivate
    cd ..
    timeout /t 5 /nobreak >nul
    set "STARTED_BACKEND=1"
) else (
    echo   + Backend already running
    set "STARTED_BACKEND=0"
)

REM Run integration tests (using the existing test_system.bat logic)
echo   -> Running integration tests...
curl -s http://localhost:8010/health >nul 2>&1
if errorlevel 1 (
    echo   X Integration tests failed - API not responding
    set /a FAILED_TESTS+=1
) else (
    echo   + API health check passed
    
    echo   ^-^> Testing project creation...
    curl -s -X POST "http://localhost:8010/api/v1/projects" ^
         -H "Content-Type: application/json" ^
         -d "{\"title\":\"Test Integration Project\",\"description\":\"Test project for CI\"}" >nul 2>&1
    if errorlevel 1 (
        echo   X Project creation test failed
        set /a FAILED_TESTS+=1
    ) else (
        echo   + Project creation test passed
    )
    
    echo   ^-^> Testing AI service health...
    curl -s "http://localhost:8010/api/v1/ai/health" >nul 2>&1
    if errorlevel 1 (
        echo   ! AI service test failed ^(expected if Ollama not running^)
    ) else (
        echo   + AI service responding
    )
)

REM Stop temporary backend if we started it
if "%STARTED_BACKEND%"=="1" (
    echo   -> Stopping temporary backend...
    taskkill /F /FI "WINDOWTITLE eq Test Backend*" >nul 2>&1
)

echo.
echo [4/4] Test Summary
echo.

if "%FAILED_TESTS%"=="0" (
    echo ========================================
    echo   ALL TESTS PASSED! [PASS]
    echo ========================================
    echo.
    echo Coverage reports generated:
    echo  - Backend: backend\coverage_backend\index.html
    echo  - Desktop: desktop\coverage_desktop\index.html
    echo.
    echo The system is ready for development!
) else (
    echo ========================================
    echo   %FAILED_TESTS% TEST SUITE^(S^) FAILED [FAIL]
    echo ========================================
    echo.
    echo Please review the test output above and
    echo fix any failing tests before deploying.
    echo.
    exit /b 1
)

echo.
pause 