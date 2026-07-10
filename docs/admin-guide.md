# Руководство администратора CMS

## Вход

- URL: `https://ekontaktor.ru/manage/`
- Роли: **editor** (контент, каталог), **manager** (заявки, экспорт)

## Каталог

1. **Категории** — дерево MPTT, slug для URL.
2. **Гroups (ProductGroup)** — карточка товара на сайте.
3. **Variants (SKU)** — исполнение, напряжение катушки, цена, флаг `is_default`.
4. Импорт: **Импорт каталога** (XLSX) — см. [import-guide.md](./import-guide.md).

## Заявки

- Список **QuoteRequest** — статусы, PDF, экспорт CSV/XLSX.
- Email уведомления: `ORDER_EMAILS` в настройках.

## Контент

- **Pages** — статические страницы (about, contacts, …).
- **News** — новости с `published_at`.
- **SiteSettings** — телефоны, Metrika ID, GA4 ID.

## SEO

- **Redirects** — 301 со старых URL.
- Sitemap генерируется ежедневно (Celery beat) и доступен на `/sitemap.xml`.
- Импорт редиректов: `python manage.py import_redirects data/redirects.csv`

## Безопасность

- 2FA (TOTP) для staff-пользователей рекомендуется.
- Загрузка документов: только разрешённые MIME (PDF, JPEG, PNG, WebP, DWG).
