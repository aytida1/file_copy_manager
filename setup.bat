@echo off
echo ================================================
echo File Copy Manager Setup
echo ================================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher
    pause
    exit /b 1
)

echo Python found. Setting up virtual environment...

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
) else (
    echo Virtual environment already exists.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo Installing requirements...
if exist "requirements.txt" (
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install requirements
        pause
        exit /b 1
    )
) else (
    echo No requirements.txt found, skipping package installation.
)

echo.
echo ================================================
echo Setup completed successfully!
echo ================================================
echo.
echo To run the file copy manager:
echo 1. Double-click on 'run_file_copy_manager.bat'
echo    OR
echo 2. Run the following commands:
echo    - venv\Scripts\activate.bat
echo    - python file_copy_manager.py
echo.

pause
