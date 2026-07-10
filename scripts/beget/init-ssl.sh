#!/usr/bin/env bash
# Первичное получение SSL-сертификата Let's Encrypt
# Запускать из корня проекта: bash scripts/beget/init-ssl.sh
set -euo pipefail

cd "$(dirname "$0")/../.."
COMPOSE="docker compose -f docker-compose.prod.yml -f docker-compose.prod.beget.yml"
EMAIL="${CERTBOT_EMAIL:-admin@ekontaktor.ru}"

echo "==> 1. HTTP-конфиг nginx (для проверки домена)"
cp nginx/nginx.prod.bootstrap.conf nginx/nginx.prod.conf
$COMPOSE up -d db redis backend frontend nginx

echo "==> 2. Запрос сертификата (ekontaktor.ru + www)"
$COMPOSE run --rm certbot certonly --webroot \
  -w /var/www/certbot \
  -d ekontaktor.ru \
  -d www.ekontaktor.ru \
  --email "$EMAIL" \
  --agree-tos \
  --no-eff-email

echo "==> 3. Восстановите HTTPS-конфиг:"
echo "    git checkout nginx/nginx.prod.conf"
echo "    $COMPOSE restart nginx certbot"
echo "==> Затем проверьте: https://www.ekontaktor.ru/"
