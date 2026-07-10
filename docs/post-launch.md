# Post-launch checklist (STEP-112)

## Search engines

1. Добавить сайт в [Yandex Webmaster](https://webmaster.yandex.ru/) и отправить sitemap `https://www.ekontaktor.ru/sitemap.xml`
2. Добавить property в [Google Search Console](https://search.google.com/search-console) и отправить sitemap

## Monitoring

- Sentry DSN в production `.env`
- Ежедневный бэкап БД: `scripts/backup-db.sh` (cron 02:00)
- Логи 404 в nginx → новые записи в `Redirect` model

## Handover

- [admin-guide.md](./admin-guide.md) — для контент-менеджеров
- [import-guide.md](./import-guide.md) — для импорта каталога
- [UAT-CHECKLIST.md](./UAT-CHECKLIST.md) — подписанный UAT

## Phase 2 backlog

- Английская версия сайта
- Elasticsearch вместо trigram
- Интеграция 1C
- Telegram-бот для заявок

**DoD:** индексация основных страниц в течение 7 дней после submit sitemap.
