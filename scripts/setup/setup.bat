@echo off
echo MCP HF Hackathon - Quick Setup for Windows
echo ==========================================

echo.
echo Setting up virtual environment...
if not exist "venv" (
    python -m venv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment
        pause
        exit /b 1
    )
)

echo.
echo Activating virtual environment and installing requirements...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Error: Failed to activate virtual environment
    pause
    exit /b 1
)

echo.
echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Installing requirements...
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install requirements
    pause
    exit /b 1
)

echo.
echo Creating necessary directories...
if not exist "logs" mkdir logs
if not exist "data\models" mkdir data\models
if not exist "data\cache" mkdir data\cache

echo.
echo Setup completed successfully!
echo.
echo To run the application:
echo 1. Activate virtual environment: venv\Scripts\activate.bat
echo 2. Run the app: python app.py
echo 3. Open browser to: http://localhost:7860
echo.
pause
