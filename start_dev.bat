@echo off
echo Starting AI Social Media Manager Development Environment...

echo.
echo Starting FastAPI Backend...
start "FastAPI Backend" cmd /k "cd api && python main.py"

echo.
echo Waiting for backend to start...
ping 127.0.0.1 -n 4 > nul

echo.
echo Starting React Frontend...
start "React Frontend" cmd /k "cd frontend && npm start"

echo.
echo Development servers are starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Press any key to exit...
pause > nul