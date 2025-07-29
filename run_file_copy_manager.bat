@echo off
echo ================================================
echo File Copy Manager
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
echo Starting File Copy Manager...
python file_copy_manager.py

echo.
echo Script execution completed.
pause
