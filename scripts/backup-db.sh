#!/usr/bin/env bash
# Daily PostgreSQL backup (STEP-111). Cron: 0 2 * * * /opt/ekontaktor/scripts/backup-db.sh
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-/var/backups/ekontaktor}"
RETENTION_DAYS="${RETENTION_DAYS:-14}"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
FILENAME="ekontaktor_${TIMESTAMP}.sql.gz"

mkdir -p "$BACKUP_DIR"

docker compose -f "${COMPOSE_FILE:-docker-compose.prod.yml}" exec -T db \
  pg_dump -U "${POSTGRES_USER:-ekontaktor}" "${POSTGRES_DB:-ekontaktor}" \
  | gzip > "${BACKUP_DIR}/${FILENAME}"

find "$BACKUP_DIR" -name 'ekontaktor_*.sql.gz' -mtime +"${RETENTION_DAYS}" -delete

echo "Backup saved: ${BACKUP_DIR}/${FILENAME}"
