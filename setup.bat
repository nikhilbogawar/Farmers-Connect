@echo off
REM FarmersConnect Quick Setup Script for Windows
REM This script automates the initial setup of the application

echo.
echo ========================================
echo   FarmersConnect Setup Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://www.python.org/
    pause
    exit /b 1
)

echo [✓] Python found
echo.

REM Create virtual environment
echo Creating virtual environment...
if exist venv (
    echo Virtual environment already exists. Skipping creation.
) else (
    python -m venv venv
    echo [✓] Virtual environment created
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo [✓] Virtual environment activated
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip wheel setuptools >nul 2>&1
echo [✓] pip upgraded
echo.

REM Install requirements
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Installation failed. Please check your internet connection.
    pause
    exit /b 1
)
echo [✓] Dependencies installed
echo.

REM Create .env file if it doesn't exist
if exist .env (
    echo .env file already exists
) else (
    echo Creating .env file...
    copy .env.example .env
    echo [✓] .env file created (please edit with your settings)
)
echo.

REM Initialize database
echo Initializing database...
python app.py init-db
echo [✓] Database initialized
echo.

REM Create demo user
echo Creating demo user...
echo If prompted, choose to create demo user
python app.py create-demo-user
echo [✓] Demo user setup complete
echo.

echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo To start the application, run:
echo   python app.py
echo.
echo The application will be available at:
echo   http://localhost:5000
echo.
echo Demo Credentials:
echo   Username: demo_farmer
echo   Password: demo_password_123
echo.
pause
