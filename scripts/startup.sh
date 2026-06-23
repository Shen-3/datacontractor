#!/bin/bash
# DataContractor — container startup script.
#
# Runs database migrations, then starts the uvicorn server.
# Intended as the CMD / entrypoint in the production Docker image.

set -euo pipefail

echo "==> Running Alembic migrations..."
alembic upgrade head

echo "==> Starting uvicorn server..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${UVICORN_PORT:-8000}"
