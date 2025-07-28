@echo off
cls
echo.
echo ========================================
echo   Motivate.AI - Quick Test Suite
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

echo [1/3] Testing Backend - Simple Tests...
echo.

cd backend
call venv\Scripts\activate.bat

echo   ^-^> Running quick import and basic functionality tests...
pytest tests/test_simple.py tests/test_endpoints_simple.py tests/test_database_simple.py tests/test_live_api.py -v
if errorlevel 1 (
    echo   X Basic backend tests failed
    set /a FAILED_TESTS+=1
) else (
    echo   + Basic backend tests passed
)

call deactivate
cd ..

echo.
echo [2/3] Testing Desktop App...
echo.

cd desktop
call venv\Scripts\activate.bat

echo   ^-^> Running desktop tests...
pytest tests/ -v
if errorlevel 1 (
    echo   X Desktop tests failed
    set /a FAILED_TESTS+=1
) else (
    echo   + Desktop tests passed
)

call deactivate
cd ..

echo.
echo [3/3] Quick Integration Check...
echo.

echo   ^-^> Checking if backend can start...
cd backend
call venv\Scripts\activate.bat
timeout /t 2 /nobreak >nul
python -c "from main import app; print('Backend app can be created successfully')" 2>nul
if errorlevel 1 (
    echo   X Backend app creation failed
    set /a FAILED_TESTS+=1
) else (
    echo   + Backend app creation successful
)
call deactivate
cd ..

echo.
echo ========================================
if "%FAILED_TESTS%"=="0" (
    echo   ALL QUICK TESTS PASSED! [PASS]
    echo.
    echo   Ready for development!
    echo   Run 'dev_start.bat' to start the full system
) else (
    echo   %FAILED_TESTS% TEST SUITE^(S^) FAILED [FAIL]
    echo.
    echo   Please fix the issues above before continuing
)
echo ========================================
echo.
pause 