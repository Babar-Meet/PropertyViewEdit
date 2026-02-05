@echo off
setlocal
echo ==========================================
echo   Time Weaver - Setup Assistant
echo ==========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not found in PATH.
    echo.
    echo Please install Python 3.9+ from:
    echo https://www.python.org/downloads/
    echo.
    echo During installation, make sure to check:
    echo [X] Add Python to PATH
    echo.
    pause
    exit /b 1
)

:: Check Python version
for /f "tokens=2" %%I in ('python --version 2^>^&1') do set PYVER=%%I
echo [INFO] Found Python %PYVER%

:: Create virtual environment
echo [1/3] Setting up virtual environment...
if exist "venv" (
    echo Virtual environment already exists, skipping...
) else (
    python -m venv venv
)

:: Install dependencies
echo [2/3] Installing dependencies...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt

:: Build executable
echo [3/3] Building standalone application...
pip install pyinstaller

echo Creating executable... This may take a few minutes.
pyinstaller --onefile --windowed --name "TimeWeaver" --icon "icon.ico" ^
    --add-data "*.py;." ^
    --hidden-import win32timezone ^
    --hidden-import win32com ^
    --hidden-import pythoncom ^
    main.py

if %errorlevel% neq 0 (
    echo.
    echo [WARNING] Could not create single executable.
    echo You can still run the application using 'run_app.bat'
) else (
    echo.
    echo [SUCCESS] Setup complete!
    echo.
    echo You can now:
    echo 1. Run the standalone app: dist\TimeWeaver.exe
    echo 2. Or use the Python version: run_app.bat
    echo.
)

pause