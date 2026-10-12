#!/bin/sh
# Long-running certbot: renew Let's Encrypt certs and reload nginx when renewed.
set -e

RENEW_INTERVAL="${RENEW_INTERVAL:-12h}"

trap 'exit 0' TERM INT

while :; do
  echo "$(date '+%Y-%m-%d %H:%M:%S') certbot renew start"
  certbot renew \
    --webroot -w /var/www/certbot \
    --quiet \
    --no-random-sleep-on-renew \
    --deploy-hook /usr/local/bin/reload-nginx-hook.sh \
    || echo "$(date '+%Y-%m-%d %H:%M:%S') certbot renew failed (will retry in ${RENEW_INTERVAL})"

  sleep "$RENEW_INTERVAL" &
  wait $!
done
