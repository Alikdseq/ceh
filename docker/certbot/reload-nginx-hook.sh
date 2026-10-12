#!/bin/sh
# Runs inside certbot container after a successful certificate renewal.
set -e

NGINX_CONTAINER="${NGINX_CONTAINER:-ekontaktor-nginx}"

if [ ! -S /var/run/docker.sock ]; then
  echo "$(date '+%Y-%m-%d %H:%M:%S') ERROR: /var/run/docker.sock is not mounted — cannot reload nginx"
  exit 1
fi

docker exec "$NGINX_CONTAINER" nginx -s reload
echo "$(date '+%Y-%m-%d %H:%M:%S') nginx reloaded (${NGINX_CONTAINER}) after certificate renewal"
