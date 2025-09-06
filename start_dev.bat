@echo off
echo Starting AI Social Media Manager Development Environment...

echo.
echo Starting FastAPI Backend...
start "FastAPI Backend" cmd /k "cd api && python main.py"

echo.
echo Waiting for backend to be ready...
timeout /t 3 /nobreak
echo Backend is ready!

echo.
echo Starting React Frontend...
start "React Frontend" cmd /k "cd frontend && npm start"

echo.
echo Development servers are ready!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo Performance: http://localhost:8000/performance/health
echo.
echo Press any key to exit...
pause > nul