#!/usr/bin/env bash
# One-shot SSL renew + nginx reload (for cron on the VPS).
# The certbot container also renews automatically; this script is a backup.
#
# Usage: bash scripts/beget/renew-ssl.sh
# Cron:  0 3 * * * /opt/ekontaktor/scripts/beget/renew-ssl.sh >> /var/log/ekontaktor-ssl-renew.log 2>&1
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

COMPOSE="docker compose -f docker-compose.prod.yml -f docker-compose.prod.beget.yml"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] SSL renew start"

$COMPOSE run --rm --entrypoint certbot certbot renew \
  --webroot -w /var/www/certbot \
  --quiet \
  --no-random-sleep-on-renew

echo "[$(date -Iseconds)] Reloading nginx"
$COMPOSE exec -T nginx nginx -s reload

echo "[$(date '+%Y-%m-%d %H:%M:%S')] SSL renew done"
