@echo off
setlocal
echo =====================================================
echo    Time Weaver - One-Click Executable Creator
echo =====================================================
echo.
echo This will create a single .exe file that can run on
echo ANY Windows computer without installing Python or Qt.
echo.
echo Press any key to begin...
pause >nul

:: Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python is not installed!
    echo.
    echo Please install Python 3.9+ from python.org
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

:: Create and activate virtual environment
echo.
echo Step 1: Setting up environment...
python -m venv build_env
call build_env\Scripts\activate.bat

:: Upgrade pip
echo.
echo Step 2: Installing tools...
pip install --upgrade pip

:: Install requirements
python -m pip install -r requirements.txt

:: Build the executable
echo.
echo Step 3: Building executable (this takes 2-5 minutes)...
python build.py

:: Clean up
echo.
echo Step 4: Cleaning up...
deactivate
rmdir /s /q build_env

:: Create final package
if exist "dist\TimeWeaver.exe" (
    mkdir "TimeWeaver_Portable" 2>nul
    copy "dist\TimeWeaver.exe" "TimeWeaver_Portable\"
    copy "README.md" "TimeWeaver_Portable\" 2>nul
    
    echo.
    echo ✅ SUCCESS!
    echo.
    echo Your standalone executable is in the "TimeWeaver_Portable" folder.
    echo.
    echo To distribute to clients:
    echo 1. Zip the "TimeWeaver_Portable" folder
    echo 2. Send the zip file
    echo 3. Clients just extract and run TimeWeaver.exe
    echo.
    echo No Python, Qt, or any other installation needed!
) else (
    echo.
    echo ❌ ERROR: Build failed!
    echo Check the error messages above.
)

echo.
pause
