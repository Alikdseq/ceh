#!/bin/sh
# Production container entrypoint — avoids heavy collectstatic on every restart.
set -e

echo "==> migrate"
python manage.py migrate --noinput

echo "==> setup_groups"
python manage.py setup_groups

STATIC_MARKER=/app/staticfiles/.collectstatic-done
if [ ! -f "$STATIC_MARKER" ]; then
  echo "==> collectstatic (first run)"
  python manage.py collectstatic --noinput
  touch "$STATIC_MARKER"
else
  echo "==> collectstatic skipped (already done)"
fi

echo "==> gunicorn"
exec gunicorn config.wsgi:application -c /app/gunicorn.conf.py
