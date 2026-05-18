#!/bin/sh
set -e

case "${SERVICE_ROLE:-web}" in
  web)
    alembic upgrade head
    python -m app.db.seed
    exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
    ;;
  all)
    alembic upgrade head
    python -m app.db.seed
    celery -A app.workers.celery_app.celery_app worker --loglevel="${LOG_LEVEL:-INFO}" --concurrency="${CELERY_CONCURRENCY:-1}" &
    worker_pid="$!"
    celery -A app.workers.celery_app.celery_app beat --loglevel="${LOG_LEVEL:-INFO}" &
    beat_pid="$!"
    trap 'kill "$worker_pid" "$beat_pid" 2>/dev/null || true' INT TERM EXIT
    exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
    ;;
  worker)
    exec celery -A app.workers.celery_app.celery_app worker --loglevel="${LOG_LEVEL:-INFO}" --concurrency="${CELERY_CONCURRENCY:-2}"
    ;;
  scheduler)
    exec celery -A app.workers.celery_app.celery_app beat --loglevel="${LOG_LEVEL:-INFO}"
    ;;
  *)
    echo "Unknown SERVICE_ROLE: ${SERVICE_ROLE}" >&2
    exit 1
    ;;
esac
