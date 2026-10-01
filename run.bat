@echo off
REM Start the PARIKSHAK-AI proof of concept on http://localhost:8000
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  py -3 -m venv .venv
  .venv\Scripts\python -m pip install -q --upgrade pip
  .venv\Scripts\python -m pip install -q -r backend\requirements.txt
)
echo Examiner workspace: http://localhost:8000/   CoE command centre: http://localhost:8000/coe
.venv\Scripts\python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000
