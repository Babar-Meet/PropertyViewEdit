@echo off
setlocal
echo ==========================================
echo   Time Weaver - Setup
echo ==========================================

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    pause
    exit /b 1
)

:: Create virtual environment if it doesn't exist
if not exist "changedate" (
    echo [INFO] Creating virtual environment...
    python -m venv changedate
)

:: Install requirements
echo [INFO] Installing dependencies...
call changedate\Scripts\activate.bat
pip install -r requirements.txt

echo.
echo [SUCCESS] Setup complete! 
echo Run the app using 'run_app.bat'.
echo.
pause
