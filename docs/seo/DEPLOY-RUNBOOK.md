# SEO deploy runbook — ekontaktor.ru

Выполнять на prod-сервере (`/opt/ekontaktor`) после выкладки SEO-изменений.

## 1. Deploy

```bash
git pull
docker compose -f docker-compose.prod.yml -f docker-compose.prod.beget.yml build backend frontend
docker compose -f docker-compose.prod.yml -f docker-compose.prod.beget.yml up -d backend frontend celery-worker celery-beat
```

## 2. Migrations и данные

```bash
docker compose -f docker-compose.prod.yml -f docker-compose.prod.beget.yml exec backend python manage.py migrate
docker compose -f docker-compose.prod.yml -f docker-compose.prod.beget.yml exec backend python manage.py import_delivery_cities
docker compose -f docker-compose.prod.yml -f docker-compose.prod.beget.yml exec backend python manage.py seed_seo_content
docker compose -f docker-compose.prod.yml -f docker-compose.prod.beget.yml exec backend python manage.py generate_product_seo_copy
docker compose -f docker-compose.prod.yml -f docker-compose.prod.beget.yml exec backend python manage.py rebuild_search_index
docker compose -f docker-compose.prod.yml -f docker-compose.prod.beget.yml exec backend python manage.py generate_sitemap
docker compose -f docker-compose.prod.yml -f docker-compose.prod.beget.yml exec backend python manage.py sync_product_catalog_redirects
```

Опционально (если менялись URL контакторов):

```bash
docker compose exec backend python manage.py align_contactor_catalog_urls
```

## 3. IndexNow

В `.env` на prod:

```env
INDEXNOW_ENABLED=true
INDEXNOW_KEY=<случайная_строка>
```

Файл `frontend/public/<INDEXNOW_KEY>.txt` с тем же ключом внутри. Пересобрать frontend.

```bash
docker compose exec backend python manage.py ping_indexnow /
```

## 4. Поисковые системы (ручные шаги)

1. [Яндекс.Вебмастер](https://webmaster.yandex.ru): сайт `https://www.ekontaktor.ru`, sitemap `https://www.ekontaktor.ru/sitemap.xml`.
2. [Google Search Console](https://search.google.com/search-console): property + sitemap.
3. Переобход: главная, `/catalog/`, топ-20 PDP из `data/seo/semantic-core.yaml`.
4. Проверить «Покрытие» / «Индексирование» через 7–14 дней.

## 5. Smoke test

```bash
curl -I https://www.ekontaktor.ru/sitemap.xml
curl -I https://www.ekontaktor.ru/robots.txt
curl -I "https://www.ekontaktor.ru/search?q=kt6023"
```

- sitemap/robots → 200
- search с модельным запросом → redirect на PDP (если однозначный товар)

## 6. Отчёт

Шаблон: [MONTHLY-REPORT.md](./MONTHLY-REPORT.md)
