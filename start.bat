@echo off
chcp 65001 >nul
echo ============================================
echo   AI Chat - Start Script
echo ============================================
echo.

cd /d "%~dp0"

set PYTHON_PATH=E:\local_LLM\qopus\Scripts\python.exe

echo [1/4] Checking Python...
"%PYTHON_PATH%" --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found at %PYTHON_PATH%
    pause
    exit /b 1
)

echo [2/4] Installing backend dependencies...
"%PYTHON_PATH%" -m pip install -r backend/requirements.txt -q

echo [3/4] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found. Please install Node.js 18+
    pause
    exit /b 1
)

echo [4/4] Installing frontend dependencies and building...
cd frontend
call npm install
call npm run build
cd ..

echo.
echo [OK] Ready! Starting server...
echo [URL] http://localhost:8000
echo.

"%PYTHON_PATH%" -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
