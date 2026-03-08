#!/bin/sh
set -eu

AUTO_MIGRATE=${AUTO_MIGRATE:-true}
AUTO_SEED=${AUTO_SEED:-true}
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8000}

if [ "$AUTO_MIGRATE" = "true" ]; then
  echo "Running database migrations..."
  alembic upgrade head
fi

if [ "$AUTO_SEED" = "true" ]; then
  echo "Initializing default data..."
  python scripts/init_default_data.py
fi

echo "Starting backend server on ${HOST}:${PORT}"
exec uvicorn app.main:app --host "$HOST" --port "$PORT"