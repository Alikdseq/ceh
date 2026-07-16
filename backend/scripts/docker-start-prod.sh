#!/bin/sh
# Production container entrypoint — avoids heavy collectstatic on every restart.
set -e

echo "==> migrate"
python manage.py migrate --noinput

echo "==> prune_broken_product_images"
python manage.py prune_broken_product_images || echo "WARNING: prune_broken_product_images failed"

echo "==> setup_groups"
python manage.py setup_groups

echo "==> ensure_site_content"
python manage.py ensure_site_content || echo "WARNING: ensure_site_content failed (continuing startup)"

echo "==> ensure_admin_user (unlock)"
python manage.py ensure_admin_user --unlock

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
