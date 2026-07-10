# АО «Электроконтактор» — корпоративный B2B-сайт

Сайт-производитель низковольтной аппаратуры: каталог, корзина-заявка, CMS, SEO.

> **Для AI-агентов и новых разработчиков:** начните с **[AGENTS.md](./AGENTS.md)** — правила проекта и карта кодовой базы.

## Документация

| Документ | Описание |
|---|---|
| **[AGENTS.md](./AGENTS.md)** | **Правила и карта проекта для AI-агентов (читать первым)** |
| **[docs/SITE-OPISANIE.txt](./docs/SITE-OPISANIE.txt)** | Полное описание сайта и завода |
| **[TZ.md](./TZ.md)** | Полное техническое задание |
| **[PLAN.md](./PLAN.md)** | Пошаговый атомарный план реализации (75 шагов) |
| [data/CLIENT_INPUT.md](./data/CLIENT_INPUT.md) | Входные данные от заказчика (Phase 0) |
| [data/README.md](./data/README.md) | Исходники каталога для импорта |
| [docs/design/DESIGN_TZ.md](./docs/design/DESIGN_TZ.md) | **ТЗ по дизайну** (главный design-артефакт) |
| [docs/design/DESIGN_SYSTEM.md](./docs/design/DESIGN_SYSTEM.md) | Design system: краткие токены |
| [docs/infrastructure/HOSTING.md](./docs/infrastructure/HOSTING.md) | Хостинг и DNS |
| **[docs/DEPLOY-BEGET.md](./docs/DEPLOY-BEGET.md)** | **Деплой на Beget VPS (пошагово)** |

## Быстрый старт

### Docker (рекомендуется)

```bash
cp .env.example .env
docker compose up -d
```

| Сервис | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000/api/v1/ |
| Admin CMS | http://localhost:8000/manage/ |
| Swagger | http://localhost:8000/api/docs/ |
| Mailhog | http://localhost:8025 |
| Nginx | http://localhost |

### Локально (без Docker)

```bash
# Backend
cd backend
pip install -r requirements/dev.txt
set DATABASE_URL=postgres://ekontaktor:ekontaktor@localhost:5432/ekontaktor
python manage.py migrate
python manage.py setup_groups
python manage.py runserver

# Frontend
cd frontend
npm install
npm run dev
```

## Структура монорепо

```
cehsite/
├── backend/          # Django 5 + DRF
├── frontend/         # Next.js 15
├── docker/           # Dockerfiles
├── nginx/            # Reverse proxy
├── data/             # Импорт каталога
└── docs/             # Design, infra
```

## Стек

- **Backend:** Django 5.1, DRF, PostgreSQL, Redis, Celery
- **Frontend:** Next.js 15, TypeScript, Tailwind CSS 4
- **Infra:** Docker Compose, Nginx, MinIO, Mailhog

См. [TZ.md §4](./TZ.md) для полного списка технологий.











Куда заходить
Сервис	URL
Сайт (Nginx)
http://localhost
Frontend
http://localhost:3000
API
http://localhost:8000/api/v1/
Админка
http://localhost:8000/manage/
Почта (тест)
http://localhost:8025



Минимальный старт
cd C:\cehsite
Copy-Item .env.example .env
docker compose up -d --build
После первого запуска (один раз):

docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py loaddata fixtures/seed_content.json
docker compose exec backend python manage.py import_categories /data/categories.yaml
docker compose exec backend python manage.py import_pricelist /data/pricelist.csv
docker compose exec backend python manage.py rebuild_search_index
