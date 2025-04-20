@echo off
echo Pandoc PATH Configuration Tool for Document QA Agent
echo ===================================================
echo This script will add Pandoc to your system PATH permanently.
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script requires administrator privileges.
    echo Please right-click on this file and select "Run as administrator".
    echo.
    pause
    exit /b 1
)

REM Try to locate Pandoc
set PANDOC_PATH=

REM Check common installation locations
if exist "C:\Program Files\Pandoc\pandoc.exe" (
    set PANDOC_PATH=C:\Program Files\Pandoc
) else if exist "C:\Program Files (x86)\Pandoc\pandoc.exe" (
    set PANDOC_PATH=C:\Program Files (x86)\Pandoc
) else if exist "%USERPROFILE%\AppData\Local\Pandoc\pandoc.exe" (
    set PANDOC_PATH=%USERPROFILE%\AppData\Local\Pandoc
)

REM If Pandoc was not found, ask user to provide the path
if "%PANDOC_PATH%"=="" (
    echo Pandoc was not found in common installation locations.
    echo.
    echo If you have Pandoc installed, please enter the full path to the Pandoc folder
    echo Example: C:\Program Files\Pandoc
    echo.
    echo If you don't have Pandoc installed, please download it from:
    echo https://pandoc.org/installing.html
    echo.
    set /p PANDOC_PATH="Enter Pandoc folder path (or press Enter to exit): "
    
    if "%PANDOC_PATH%"=="" (
        echo Operation cancelled.
        pause
        exit /b 1
    )
    
    REM Check if the provided path contains pandoc.exe
    if not exist "%PANDOC_PATH%\pandoc.exe" (
        echo ERROR: pandoc.exe was not found in the specified directory.
        pause
        exit /b 1
    )
)

echo Found Pandoc at: %PANDOC_PATH%

REM Add Pandoc to the system PATH
setx PATH "%PATH%;%PANDOC_PATH%" /M

if %errorLevel% neq 0 (
    echo ERROR: Failed to update the system PATH.
    pause
    exit /b 1
)

echo.
echo SUCCESS: Pandoc has been added to your system PATH.
echo You may need to restart your command prompt or computer
echo for the changes to take effect.
echo.
echo After restarting, you should be able to process PowerPoint files
echo with the Document QA Agent.
echo.

pause 