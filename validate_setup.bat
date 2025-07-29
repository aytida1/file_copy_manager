@echo off
echo ================================================
echo Network Path Validation
echo ================================================

set SOURCE_PATH=\\172.16.70.71\Mechanical Data\Nishant
set DEST_PATH=\\172.16.70.71\mechanical data\Nishant\CRM V2 27-12-2018\DA03_25-1-2019 EPDM\001 DA SM\Factory layout

echo Testing network connectivity...
echo.

echo Checking source path access:
echo %SOURCE_PATH%
if exist "%SOURCE_PATH%" (
    echo ✓ Source path accessible
    dir "%SOURCE_PATH%" /b | findstr /c:"." >nul
    if errorlevel 1 (
        echo ⚠ Warning: Source path is empty or inaccessible
    ) else (
        echo ✓ Source path contains files
    )
) else (
    echo ✗ ERROR: Cannot access source path
    echo   Please check network connectivity and permissions
)

echo.
echo Checking destination path access:
echo %DEST_PATH%
if exist "%DEST_PATH%" (
    echo ✓ Destination path accessible
) else (
    echo ⚠ Destination path doesn't exist (will be created)
    
    REM Try to create a test directory
    mkdir "%DEST_PATH%\test_folder" 2>nul
    if exist "%DEST_PATH%\test_folder" (
        echo ✓ Can create directories at destination
        rmdir "%DEST_PATH%\test_folder" 2>nul
    ) else (
        echo ✗ ERROR: Cannot create directories at destination
        echo   Please check write permissions
    )
)

echo.
echo Testing CSV files:
if exist "db" (
    echo ✓ CSV directory found
    dir db\*.csv /b 2>nul | find /c /v "" >temp_count.txt
    set /p CSV_COUNT=<temp_count.txt
    del temp_count.txt
    echo ✓ Found CSV files in db directory
) else (
    echo ✗ ERROR: CSV directory 'db' not found
    echo   Please ensure the 'db' folder is in the same directory as this script
)

echo.
echo ================================================
echo Validation completed
echo ================================================
echo.
echo If all checks passed, you can proceed with running the file copy manager.
echo If there are errors, please resolve them before continuing.
echo.

pause
