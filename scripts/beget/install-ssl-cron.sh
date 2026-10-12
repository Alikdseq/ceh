#!/usr/bin/env bash
# Install daily cron job: renew SSL and reload nginx.
# Run once on the VPS as root or a user with crontab access.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
RENEW_SCRIPT="$ROOT/scripts/beget/renew-ssl.sh"
LOG_FILE="${SSL_CRON_LOG:-/var/log/ekontaktor-ssl-renew.log}"

if [ ! -x "$RENEW_SCRIPT" ]; then
  chmod +x "$RENEW_SCRIPT"
fi

CRON_LINE="0 3 * * * $RENEW_SCRIPT >> $LOG_FILE 2>&1"

if crontab -l 2>/dev/null | grep -Fq "$RENEW_SCRIPT"; then
  echo "Cron job already installed:"
  crontab -l | grep -F "$RENEW_SCRIPT"
  exit 0
fi

(crontab -l 2>/dev/null || true; echo "$CRON_LINE") | crontab -

echo "Installed cron job:"
echo "  $CRON_LINE"
echo "Log file: $LOG_FILE"
echo ""
echo "The certbot container also renews every 12h with automatic nginx reload."
echo "Cron is an extra safety net if the certbot container stops."
