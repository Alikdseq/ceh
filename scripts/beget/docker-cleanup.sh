#!/usr/bin/env bash
# Free disk space before Docker builds on small Beget VPS (10 GB disk).
set -euo pipefail

echo "==> Disk before"
df -h /

echo "==> Docker disk usage"
docker system df || true

echo "==> Build cache (often 2–5 GB)"
docker builder prune -af

echo "==> Unused images (not referenced by running containers)"
docker image prune -a -f

echo "==> Stopped containers"
docker container prune -f

echo "==> Disk after"
df -h /
docker system df || true

AVAIL=$(df -BG / | awk 'NR==2 {print $4}' | tr -d G)
if [ "${AVAIL:-0}" -lt 2 ] 2>/dev/null; then
  echo "WARNING: less than 2 GB free — frontend build may still fail."
  echo "Consider: apt clean, journalctl --vacuum-size=100M, or larger disk in Beget panel."
else
  echo "OK: ${AVAIL}G free — you can run: docker compose ... build frontend"
fi
