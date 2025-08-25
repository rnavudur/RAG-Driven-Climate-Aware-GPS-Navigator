@echo off
echo ========================================
echo Climate-Aware GPS Navigator Setup
echo ========================================
echo.

echo Installing dependencies...
npm install

if %errorlevel% neq 0 (
    echo Error: Failed to install dependencies
    echo Please make sure Node.js and npm are installed
    pause
    exit /b 1
)

echo.
echo Dependencies installed successfully!
echo.
echo Starting development server...
echo The app will open in your browser at http://localhost:3000
echo.
echo Press Ctrl+C to stop the server
echo.

npm start

pause
