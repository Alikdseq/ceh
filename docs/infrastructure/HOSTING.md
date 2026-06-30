# Инфраструктура и хостинг

> **STEP-004** · Phase 0  
> Документ для согласования с заказчиком и DevOps.

## Рекомендуемая конфигурация

| Параметр | Рекомендация | Обоснование |
|---|---|---|
| Провайдер | **Yandex Cloud** или **Selectel** | Юрисдiction РФ, 152-ФЗ |
| VPS | 4 vCPU, 8 GB RAM, 80 GB SSD | TZ §14.2, ~100 concurrent users |
| ОС | Ubuntu 22.04 LTS | Docker, long support |
| БД | Managed PostgreSQL 16 или контейнер | Full-text search, backups |
| CDN | Yandex CDN / Cloudflare (опционально) | Static/media в prod |

## Домены

| Окружение | Домен | Назначение | Статус |
|---|---|---|---|
| Production | `ekontaktor.ru` | Основной сайт | ⚠️ Требует подтверждения |
| Staging | `staging.ekontaktor.ru` | Тестирование перед релизом | 📋 Запланировано |
| Admin | `ekontaktor.ru/manage/` | CMS (нестандартный URL) | — |

## DNS-записи (шаблон)

```
# Production
ekontaktor.ru.          A      <PROD_IP>
www.ekontaktor.ru.      CNAME  ekontaktor.ru.

# Staging
staging.ekontaktor.ru.  A      <STAGING_IP>
```

## SSL

- **Let's Encrypt** через certbot + nginx
- Автообновление сертификатов (cron)
- HSTS включить после проверки staging

## Архитектура деплоя

```
                    ┌─────────────┐
   Internet ───────►│   Nginx     │ :443 SSL
                    │  (reverse)  │
                    └──────┬──────┘
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    ┌────────────┐  ┌────────────┐  ┌────────────┐
    │  Next.js   │  │  Django    │  │   MinIO    │
    │  :3000     │  │  :8000     │  │  :9000     │
    └────────────┘  └─────┬──────┘  └────────────┘
                          │
              ┌───────────┼───────────┐
              ▼           ▼           ▼
        PostgreSQL    Redis      Celery
```

## Backup

| Объект | Частота | Хранение |
|---|---|---|
| PostgreSQL dump | Ежедневно 03:00 MSK | 30 дней |
| Media (MinIO/S3) | Еженедельно | 30 дней |
| `.env` secrets | Вне git, vault | — |

## Чеклист STEP-004

- [ ] Заказчик подтвердил домен `ekontaktor.ru`
- [ ] Создан VPS staging (4 vCPU / 8 GB)
- [ ] DNS A-record `staging.ekontaktor.ru` → staging IP
- [ ] SSH-доступ для deploy (ключи, не пароль)
- [ ] Firewall: 22, 80, 443 only

## Следующий шаг

После Phase 1: `docker compose -f docker-compose.prod.yml up -d` на staging (STEP-110).
