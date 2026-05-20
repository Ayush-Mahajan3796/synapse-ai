@echo off
echo Starting AI Research Copilot Backend and Frontend...

:: Start the Backend Server in a new command window
echo Launching Backend FastAPI server...
start "Backend API Server" cmd /k "cd backend && venv\Scripts\activate && uvicorn main:app --reload --host 127.0.0.1 --port 8000"

:: Start the Frontend Server in a new command window
echo Launching Frontend Vite dev server...
start "Frontend Vite Server" cmd /k "cd frontend && npm run dev"

echo Done! The app is booting up. 
echo - Backend will run at: http://127.0.0.1:8000
echo - Frontend will run at: http://localhost:5173/
pause
