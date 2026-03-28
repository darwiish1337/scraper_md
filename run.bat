@echo off
TITLE M-D Web Scraper
COLOR 0A

:: Check if virtual environment exists
IF NOT EXIST "Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    echo Please run 'setup.bat' first to install dependencies.
    pause
    exit /b
)

:: Run the program using the internal python
echo Starting M-D Web Scraper...
".\Scripts\python.exe" main.py

:: Keep the window open if the program finishes or crashes
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Program crashed with exit code %ERRORLEVEL%
    pause
)
