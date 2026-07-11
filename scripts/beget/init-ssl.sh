#!/usr/bin/env bash
# Первичное получение SSL Let's Encrypt для ekontaktor.ru
# Запуск: bash scripts/beget/init-ssl.sh
set -euo pipefail

cd "$(dirname "$0")/../.."
COMPOSE="docker compose -f docker-compose.prod.yml -f docker-compose.prod.beget.yml"
EMAIL="${CERTBOT_EMAIL:-admin@ekontaktor.ru}"

echo "==> 0. Проверка DNS (должен быть IP этого VPS)"
IP_EXPECT="${VPS_IP:-89.169.38.172}"
for host in ekontaktor.ru www.ekontaktor.ru; do
  IP_GOT=$(dig +short "$host" @8.8.8.8 | tail -1)
  echo "  $host -> $IP_GOT (ожидается $IP_EXPECT)"
  if [ "$IP_GOT" != "$IP_EXPECT" ]; then
    echo "ОШИБКА: DNS для $host ещё не указывает на VPS."
    echo "Смените A-запись у провайдера NS (сейчас ns*.smartape.ru) и повторите."
    exit 1
  fi
done

echo "==> 1. HTTP-конфиг nginx (bootstrap)"
cp nginx/nginx.prod.bootstrap.conf nginx/nginx.prod.conf
$COMPOSE up -d nginx

echo "==> 2. Тест webroot (том certbot_www должен быть виден nginx)"
$COMPOSE run --rm --entrypoint sh certbot -c \
  'mkdir -p /var/www/certbot/.well-known/acme-challenge && echo ok > /var/www/certbot/.well-known/acme-challenge/ping'
sleep 1
if ! curl -fsS "http://127.0.0.1/.well-known/acme-challenge/ping" -H "Host: www.ekontaktor.ru" | grep -q ok; then
  echo "ОШИБКА: nginx не отдаёт /.well-known/acme-challenge/ — проверьте том certbot_www"
  exit 1
fi
echo "  webroot OK"

echo "==> 3. Запрос сертификата"
$COMPOSE run --rm --entrypoint certbot certbot certonly \
  --webroot -w /var/www/certbot \
  -d ekontaktor.ru -d www.ekontaktor.ru \
  --email "$EMAIL" \
  --agree-tos --no-eff-email \
  --non-interactive

echo "==> 4. HTTPS-конфиг nginx"
if [ -f nginx/nginx.prod.ssl.conf.bak ]; then
  cp nginx/nginx.prod.ssl.conf.bak nginx/nginx.prod.conf
else
  git checkout nginx/nginx.prod.conf
fi
$COMPOSE up -d --force-recreate nginx certbot

echo "==> Готово: https://www.ekontaktor.ru/"
