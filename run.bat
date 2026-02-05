@echo off
setlocal
echo Time Weaver - Direct Execution
echo.

:: Check if executable exists
if exist "dist\TimeWeaver.exe" (
    echo Running standalone executable...
    echo.
    start "" "dist\TimeWeaver.exe"
    exit /b 0
)

:: Check if build exists
if not exist "build.py" (
    echo Error: build.py not found!
    pause
    exit /b 1
)

echo Standalone executable not found.
echo.
echo Would you like to build it now? (Y/N)
set /p choice=

if /i "%choice%"=="Y" (
    echo Building executable...
    python build.py
    echo.
    if exist "dist\TimeWeaver.exe" (
        echo Running the newly built executable...
        start "" "dist\TimeWeaver.exe"
    )
) else (
    echo You can build the executable later by running: python build.py
)

pause