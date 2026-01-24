#!/bin/sh
set -e

echo "Starting entrypoint: waiting for DB and applying migrations if needed..."

MAX_RETRIES=60
COUNT=0

until python manage.py migrate --noinput 2>/tmp/migrate_err; do
  COUNT=$((COUNT+1))
  echo "Migration attempt $COUNT/$MAX_RETRIES failed; waiting 1s and retrying..."
  if [ "$COUNT" -ge "$MAX_RETRIES" ]; then
    echo "Migrations failed after $MAX_RETRIES attempts. Showing last error:" >&2
    cat /tmp/migrate_err >&2 || true
    exit 1
  fi
  sleep 1
done

echo "Migrations applied successfully. Starting command..."

exec "$@"
