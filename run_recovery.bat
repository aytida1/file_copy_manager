@echo off
echo ================================================
echo Not Found Files Recovery v1.0
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

REM Run the recovery script
echo Starting Not Found Files Recovery...
echo Processing 67 missing files from not_found_files_1753824143.txt...
python process_not_found_files.py

echo.
echo Recovery script execution completed.
pause
