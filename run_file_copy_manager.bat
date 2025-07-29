@echo off
echo ================================================
echo File Copy Manager v2.0 - Multi-Source Search
echo ================================================

REM Check if virtual environment exists
if not exist "venv" (
    echo ERROR: Virtual environment not found.
    echo Please run setup.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Run the script
echo Starting Multi-Source File Copy Manager...
echo Searching up to 7 levels deep in 3 source directories...
python file_copy_manager.py

echo.
echo Script execution completed.
pause
