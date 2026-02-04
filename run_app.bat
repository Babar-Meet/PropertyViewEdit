@echo off
setlocal
echo ==========================================
echo   Time Weaver - Launching...
echo ==========================================

:: Check if venv exists
if not exist "changedate\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found. Please run 'setup.bat' first.
    pause
    exit /b 1
)

:: Run the application
call changedate\Scripts\activate.bat
python main.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Application exited with an error. 
    pause
)
