#!/usr/bin/env bash
# Обновление сайта на сервере Beget
set -euo pipefail

cd "$(dirname "$0")/../.."

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml:docker-compose.prod.beget.yml}"
export COMPOSE_FILE

echo "==> Сборка и запуск контейнеров"
docker compose up -d --build

echo "==> Миграции БД"
docker compose exec -T backend python manage.py migrate --noinput

echo "==> Импорт редиректов (если есть файл)"
if [ -f data/redirects.csv ]; then
  docker compose exec -T backend python manage.py import_redirects /data/redirects.csv || true
fi

echo "==> Пересборка поискового индекса"
docker compose exec -T backend python manage.py rebuild_search_index || true

echo "==> Готово"
docker compose ps
echo "Сайт: https://www.ekontaktor.ru/"
echo "Админка: https://www.ekontaktor.ru/manage/"
