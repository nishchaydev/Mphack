#!/usr/bin/env bash
# Start the PARIKSHAK-AI proof of concept on http://localhost:8000
set -euo pipefail
cd "$(dirname "$0")"
if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
  .venv/bin/pip install -q --upgrade pip
  .venv/bin/pip install -q -r backend/requirements.txt
fi
PORT="${PORT:-8000}"
echo "Examiner workspace: http://localhost:${PORT}/   CoE command centre: http://localhost:${PORT}/coe"
exec .venv/bin/uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port "${PORT}"
