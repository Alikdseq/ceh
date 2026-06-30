# АО «Электроконтактор» — корпоративный B2B-сайт

Сайт-производитель низковольтной аппаратуры: каталог, корзина-заявка, CMS, SEO.

## Документация

| Документ | Описание |
|---|---|
| **[TZ.md](./TZ.md)** | Полное техническое задание |
| **[PLAN.md](./PLAN.md)** | Пошаговый атомарный план реализации (75 шагов) |
| [data/CLIENT_INPUT.md](./data/CLIENT_INPUT.md) | Входные данные от заказчика (Phase 0) |
| [data/README.md](./data/README.md) | Исходники каталога для импорта |
| [docs/design/DESIGN_SYSTEM.md](./docs/design/DESIGN_SYSTEM.md) | Design system и палитра |
| [docs/infrastructure/HOSTING.md](./docs/infrastructure/HOSTING.md) | Хостинг и DNS |

## Исходные материалы

- `КАТАЛОГ КОНТАКТОРОВ 2026.pdf` — каталог продукции
- `catalog_extract.txt` — текст, извлечённый из PDF

## Быстрый старт (после Phase 1)

```bash
cp .env.example .env
docker compose up -d
```

## Стек

- **Backend:** Django 5, DRF, PostgreSQL, Redis, Celery
- **Frontend:** Next.js 15, TypeScript, Tailwind CSS
- **Infra:** Docker, Nginx

См. [TZ.md §4](./TZ.md) для полного списка технологий.
