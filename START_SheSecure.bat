@echo off
REM SheSecure - Women's Safety Application
REM Windows Startup Script

cls
echo ============================================================
echo   SheSecure - Women's Safety Application
echo ============================================================
echo.

REM Activate the virtual environment
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else (
    echo Warning: Virtual environment not found. Using system Python.
)

REM Run the Flask app
echo Starting SheSecure Server...
echo.
echo Access the application at: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server.
echo.

python run_app.py

pause
