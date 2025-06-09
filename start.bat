@echo off
REM NimbusRelay Quick Start Script
REM Imperial Purple Email Management Application

echo.
echo  🌩️  NimbusRelay - Minimalistic Email Management
echo  📧  Imperial Purple Theme - Grandeur ^& Nobility
echo ================================================

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo    Please install Python 3.9+ and try again
    pause
    exit /b 1
)

echo ✅ Python detected

REM Check if requirements.txt exists
if not exist requirements.txt (
    echo ❌ requirements.txt not found
    echo    Please ensure you're in the NimbusRelay directory
    pause
    exit /b 1
)

echo ✅ Requirements file found

REM Install dependencies
echo.
echo 📦 Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo ✅ Dependencies installed

REM Check if .env exists, if not create template
if not exist .env (
    echo.
    echo 📝 Creating .env template file...
    echo # NimbusRelay Configuration > .env
    echo # Email Configuration >> .env
    echo IMAP_SERVER= >> .env
    echo IMAP_PORT=993 >> .env
    echo IMAP_USERNAME= >> .env
    echo IMAP_PASSWORD= >> .env
    echo. >> .env
    echo # Azure OpenAI Configuration >> .env
    echo AZURE_OPENAI_ENDPOINT= >> .env
    echo AZURE_OPENAI_API_KEY= >> .env
    echo AZURE_OPENAI_DEPLOYMENT= >> .env
    echo AZURE_OPENAI_API_VERSION=2024-12-01-preview >> .env
    echo. >> .env
    echo # Application Configuration >> .env
    echo SECRET_KEY=nimbus-relay-imperial-secret >> .env
    
    echo ✅ .env template created
    echo    You can configure your credentials via the web interface
)

REM Run tests to verify everything is working
echo.
echo 🧪 Running quick validation tests...
python -m pytest src\tests\test_simple.py -v --tb=short
if %errorlevel% neq 0 (
    echo ⚠️  Some tests failed, but application may still work
) else (
    echo ✅ All tests passed
)

REM Start the application
echo.
echo 🚀 Starting NimbusRelay application...
echo.
echo    📧 Imperial Purple Email Management
echo    🌐 Opening at: http://localhost:5000
echo    ⚡ Press Ctrl+C to stop the server
echo.
echo ================================================
echo.

REM Start the Flask application
python main.py

echo.
echo 👋 NimbusRelay stopped. Thank you for using Imperial Purple email management!
pause
