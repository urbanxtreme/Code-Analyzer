@echo off
echo Starting RepoIntel Backend...
cd ..
python -m uvicorn backend.app.main:app --reload --port 8000
pause
