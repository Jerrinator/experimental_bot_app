@echo off
echo HERO Assistant Chatbot - Development Setup
echo ==========================================

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Node.js is not installed. Please install Node.js 18+ first.
    pause
    exit /b 1
)

REM Check if npm is installed
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: npm is not installed. Please install npm first.
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
npm install

REM Check if .env file exists
if not exist .env (
    echo Warning: .env file not found. Please create one with your configuration.
    echo See README.md for required environment variables.
)

REM Build the application
echo Building application...
npm run build

REM Create necessary directories
if not exist uploads mkdir uploads
if not exist temp mkdir temp
if not exist public\downloads mkdir public\downloads
if not exist logs mkdir logs

echo Setup complete! You can now start the application with:
echo   npm run dev    ^(development mode^)
echo   npm start      ^(production mode^)
echo   docker-compose up -d ^(Docker deployment^)
pause
