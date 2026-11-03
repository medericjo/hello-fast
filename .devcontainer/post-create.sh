#!/usr/bin/env bash
# Runs once, right after the dev container is created.
set -euo pipefail

python -m venv "$VIRTUAL_ENV"
pip install --upgrade pip
pip install -r requirements-dev.txt

# Create a local .env from the template if there isn't one yet.
[ -f .env ] || cp .env.example .env

echo "✅ Ready. Start the API with: uvicorn app.main:app --reload --host 0.0.0.0"
