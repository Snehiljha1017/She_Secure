@echo off
setlocal

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Virtual environment not found.
    echo Expected: .venv\Scripts\python.exe
    echo.
    pause
    exit /b 1
)

echo Starting SheSecure...
echo Open http://127.0.0.1:5000 in your browser after the server starts.
echo.

".venv\Scripts\python.exe" run_server.py

echo.
echo Server stopped.
pause
