@echo off
TITLE M-D Scraper Setup
COLOR 0B

echo ========================================
echo       M-D Web Scraper — Setup
echo ========================================
echo.

:: 1. Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found in PATH! Please install Python 3.
    pause
    exit /b
)

:: 2. Create Venv in current directory (Root)
echo [1/3] Creating Virtual Environment in root...
python -m venv .

:: 3. Upgrade Pip
echo [2/3] Upgrading Pip...
".\Scripts\python.exe" -m pip install --upgrade pip

:: 4. Install Requirements
echo [3/3] Installing Dependencies from requirements.txt...
".\Scripts\pip.exe" install -r requirements.txt

echo.
echo ========================================
echo       Setup Completed Successfully!
echo ========================================
echo.
echo You can now start the program using 'run.bat'
pause
