@echo off
echo =======================================
echo Starting AI Flight Assistant BACKEND
echo =======================================
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
pause
