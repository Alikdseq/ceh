#!/bin/sh
# Verify backend image contains admin media fixes (run on server in repo root).
set -e
cd "$(dirname "$0")/.."
echo "Git:" && git log -1 --oneline
echo "Checking admin.py for inline image cleanup..."
grep -q "get_queryset" backend/apps/products/admin.py && grep -q "image_file_exists" backend/apps/products/admin.py
grep -q "prune_broken_product_images" backend/scripts/docker-start-prod.sh
echo "OK: admin product media fixes present in checkout."
echo "Run: docker compose -f docker-compose.prod.yml -f docker-compose.prod.beget.yml build backend --no-cache"
echo "     docker compose -f docker-compose.prod.yml -f docker-compose.prod.beget.yml up -d backend"
echo "     docker compose -f docker-compose.prod.yml -f docker-compose.prod.beget.yml exec backend python manage.py migrate"
echo "     docker compose -f docker-compose.prod.yml -f docker-compose.prod.beget.yml exec backend python manage.py prune_broken_product_images"
echo "     docker compose -f docker-compose.prod.yml -f docker-compose.prod.beget.yml exec backend python manage.py recreate_all_broken_product_groups --dry-run"
echo "     docker compose -f docker-compose.prod.yml -f docker-compose.prod.beget.yml exec backend python manage.py recreate_all_broken_product_groups"
