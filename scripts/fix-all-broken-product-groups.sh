#!/bin/sh
# Recreate all catalog cards with orphan ProductImage rows (admin 500). Run on prod in repo root.
set -e
cd "$(dirname "$0")/.."
COMPOSE="docker compose -f docker-compose.prod.yml -f docker-compose.prod.beget.yml"
echo "==> Dry run (list affected groups)"
$COMPOSE exec -T backend python manage.py recreate_all_broken_product_groups --dry-run
echo ""
read -p "Apply recreate for all listed groups? [y/N] " ans
case "$ans" in
  y|Y|yes|YES) ;;
  *) echo "Aborted."; exit 0 ;;
esac
echo "==> Recreate all"
$COMPOSE exec -T backend python manage.py recreate_all_broken_product_groups
echo "==> Prune any leftover broken rows"
$COMPOSE exec -T backend python manage.py prune_broken_product_images
echo "Done."
