@echo off

rem AI File Management Tool - Start Script
rem Version: 1.0.0
rem Function: Check Python environment, install dependencies, start main program

echo ========================================
echo      AI File Management Tool
echo ========================================
echo.

rem Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python environment not found
    echo Please install Python 3.8 or higher first
    echo.
    echo You can download it from:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo Python environment found

rem Check if dependencies need to be installed
if not exist ".installed" (
    echo First run, installing dependencies...
    echo.

    rem Install dependencies
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo Error: Failed to install dependencies
        echo Please check network connection or install dependencies manually
        echo.
        pause
        exit /b 1
    )

    rem Create installation marker file
    echo Dependencies installed successfully > .installed
    echo.
)

echo Dependencies check completed

rem Start main program (default: start GUI interface)
echo Starting AI File Management Tool...
echo.
echo Tip: Press Ctrl+C to exit the program
echo.
python -c "from src.gui import run_gui; run_gui()"

rem Check program exit status
if %errorlevel% neq 0 (
    echo.
    echo Error: Program failed to start
    echo Please check error messages and try to resolve
    echo.
    pause
    exit /b 1
)

echo.
echo Program exited
pause