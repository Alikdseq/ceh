# Деплой на Beget VPS — https://www.ekontaktor.ru

Пошаговая инструкция для размещения сайта АО «Электроконтактор» на виртуальном сервере [Beget](https://beget.com/).

---

## 1. Какой сервер нужен

### Краткий ответ про тариф «1 ядро / 1 ГБ / 10 ГБ NVMe» (~11 ₽/день)

| Параметр | Вердикт |
|---|---|
| **1 ГБ RAM** | ⚠️ **На грани.** Сайт запустится в облегчённом режиме (`docker-compose.prod.beget.yml`), но при пиках (сборка, импорт каталога, несколько пользователей) возможны подвисания. **Обязательно** добавьте swap 1–2 ГБ. |
| **10 ГБ диск** | ✅ **Хватит** для старта: ОС + Docker + БД + медиа. Следите за местом (`df -h`). Фото товаров лучше не заливать сотнями мегабайт без нужды. |
| **1 ядро CPU** | ✅ **Достаточно** для B2B-каталога с умеренным трафиком (десятки одновременных посетителей). |

### Рекомендация

| Вариант | RAM | Когда брать |
|---|---|---|
| **Минимум (ваш тариф)** | 1 ГБ + swap | Тестовый запуск, мало посетителей, экономия |
| **Рекомендуемый** | **2 ГБ** | Стабильная работа без swap, комфортная сборка Docker |
| **Комфортный** | 4 ГБ | Рост каталога, активная админка, резерв |

> **Важно:** обычный **виртуальный хостинг Beget** (без root/Docker) **не подходит** — нужен именно **VPS** с Ubuntu и root-доступом.

---

## 2. Что будет установлено

```
Интернет → Nginx (443 SSL) → Next.js (фронт)
                           → Django (API + админка /manage/)
                           → PostgreSQL + Redis + Celery
```

| URL | Назначение |
|---|---|
| https://www.ekontaktor.ru/ | Главная, каталог, заявки |
| https://www.ekontaktor.ru/manage/ | Админ-панель |
| https://www.ekontaktor.ru/api/v1/ | API |
| https://ekontaktor.ru/ | Редirect → www |

---

## 3. Подготовка домена (DNS)

В панели Beget (или у регистратора домена) создайте записи:

| Имя | Тип | Значение |
|---|---|---|
| `@` (ekontaktor.ru) | **A** | IP вашего VPS |
| `www` | **A** | IP вашего VPS |

> Либо `www` → **CNAME** → `ekontaktor.ru`, если Beget так удобнее.

Дождитесь обновления DNS (5–60 минут). Проверка:

```bash
ping ekontaktor.ru
ping www.ekontaktor.ru
```

---

## 4. Подготовка VPS (один раз)

### 4.1. Подключение по SSH

```bash
ssh root@ВАШ_IP
```

Пароль/root — из панели Beget VPS.

### 4.2. Обновление системы

```bash
apt update && apt upgrade -y
apt install -y git curl ufw
```

### 4.3. Swap (обязательно для тарифа 1 ГБ)

```bash
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
free -h
```

### 4.4. Установка Docker

```bash
curl -fsSL https://get.docker.com | sh
systemctl enable docker
systemctl start docker
docker compose version
```

### 4.5. Firewall

```bash
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
ufw status
```

### 4.6. Папка проекта

```bash
mkdir -p /opt/ekontaktor
cd /opt/ekontaktor
```

---

## 5. Загрузка кода на сервер

### Вариант A — Git (рекомендуется)

```bash
cd /opt/ekontaktor
git clone https://github.com/ВАШ_АККАУНТ/cehsite.git .
```

### Вариант B — архив с локального ПК

На Windows (PowerShell):

```powershell
cd C:\cehsite
git archive -o ekontaktor-deploy.zip HEAD
scp ekontaktor-deploy.zip root@ВАШ_IP:/opt/ekontaktor/
```

На сервере:

```bash
cd /opt/ekontaktor
apt install -y unzip
unzip ekontaktor-deploy.zip
```

---

## 6. Настройка окружения (.env)

```bash
cd /opt/ekontaktor
cp .env.production.example .env
nano .env
```

**Обязательно замените:**

| Переменная | Что указать |
|---|---|
| `SECRET_KEY` | Случайная строка 50+ символов |
| `POSTGRES_PASSWORD` | Сильный пароль (и в `DATABASE_URL`) |
| `DJANGO_SUPERUSER_PASSWORD` | Пароль админа (смените после входа!) |
| `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` | SMTP Beget или корпоративная почта |

Проверьте домены:

```env
FRONTEND_URL=https://www.ekontaktor.ru
NEXT_PUBLIC_SITE_URL=https://www.ekontaktor.ru
NEXT_PUBLIC_API_URL=https://www.ekontaktor.ru/api/v1
```

---

## 7. Первый запуск

### 7.1. Сборка и старт (облегчённый режим для 1–2 ГБ RAM)

```bash
cd /opt/ekontaktor
docker compose -f docker-compose.prod.yml -f docker-compose.prod.beget.yml up -d --build
```

Первая сборка занимает **15–40 минут** на слабом VPS — это нормально.

### 7.2. SSL-сертификат (HTTPS)

**Шаг 1** — временно HTTP-конфиг:

```bash
cp nginx/nginx.prod.bootstrap.conf nginx/nginx.prod.conf
docker compose -f docker-compose.prod.yml -f docker-compose.prod.beget.yml up -d nginx
```

**Шаг 2** — получить сертификат:

```bash
docker compose -f docker-compose.prod.yml -f docker-compose.prod.beget.yml run --rm certbot certonly \
  --webroot -w /var/www/certbot \
  -d ekontaktor.ru -d www.ekontaktor.ru \
  --email admin@ekontaktor.ru \
  --agree-tos --no-eff-email
```

**Шаг 3** — вернуть HTTPS-конфиг из репозитория:

```bash
git checkout nginx/nginx.prod.conf
# или скопируйте файл nginx/nginx.prod.conf из архива заново
docker compose -f docker-compose.prod.yml -f docker-compose.prod.beget.yml restart nginx certbot
```

### 7.3. Создание администратора

```bash
docker compose -f docker-compose.prod.yml -f docker-compose.prod.beget.yml exec backend \
  python manage.py ensure_admin_user
```

Либо интерактивно:

```bash
docker compose -f docker-compose.prod.yml -f docker-compose.prod.beget.yml exec backend \
  python manage.py createsuperuser
```

---

## 8. Импорт данных каталога

После первого запуска:

```bash
# Категории
docker compose exec backend python manage.py import_categories /data/categories.csv

# Каталог из текста (если есть файл)
docker compose exec backend python manage.py import_catalog_text /data/тексткаталога.txt

# Прайс-лист
docker compose exec backend python manage.py import_pricelist /data/pricelist.csv

# Поисковый индекс
docker compose exec backend python manage.py rebuild_search_index
```

> Файлы должны лежать в папке `data/` на сервере (она монтируется в контейнер как `/data`).

---

## 9. Проверка после деплоя

| Проверка | Команда / URL |
|---|---|
| Главная | https://www.ekontaktor.ru/ |
| Каталог | https://www.ekontaktor.ru/catalog/ |
| Прайс | https://www.ekontaktor.ru/pricelist |
| API | https://www.ekontaktor.ru/api/v1/categories/ |
| Админка | https://www.ekontaktor.ru/manage/ |
| Sitemap | https://www.ekontaktor.ru/sitemap.xml |
| Редirect www | https://ekontaktor.ru/ → www |
| SSL | https://www.ssllabs.com/ssltest/ |

Статус контейнеров:

```bash
docker compose -f docker-compose.prod.yml -f docker-compose.prod.beget.yml ps
docker compose logs -f --tail=50 nginx backend frontend
```

---

## 10. Обновление сайта (повторный деплой)

```bash
cd /opt/ekontaktor
git pull
bash scripts/beget/deploy.sh
```

Или вручную:

```bash
docker compose -f docker-compose.prod.yml -f docker-compose.prod.beget.yml up -d --build
docker compose exec -T backend python manage.py migrate --noinput
```

---

## 11. Резервное копирование

Ежедневный бэкап БД (cron):

```bash
chmod +x scripts/backup-db.sh
crontab -e
```

Добавьте строку:

```cron
0 3 * * * COMPOSE_FILE=docker-compose.prod.yml:docker-compose.prod.beget.yml /opt/ekontaktor/scripts/backup-db.sh >> /var/log/ekontaktor-backup.log 2>&1
```

---

## 12. Почта на Beget

Пример SMTP в `.env`:

```env
EMAIL_HOST=smtp.beget.com
EMAIL_PORT=465
EMAIL_USE_SSL=True
EMAIL_USE_TLS=False
EMAIL_HOST_USER=noreply@ekontaktor.ru
EMAIL_HOST_PASSWORD=пароль-из-панели-beget
DEFAULT_FROM_EMAIL=noreply@ekontaktor.ru
ORDER_EMAILS=info@ekontaktor.ru
```

Создайте ящик `noreply@ekontaktor.ru` в панели Beget → Почта.

---

## 13. Частые проблемы

| Симптом | Решение |
|---|---|
| Сайт не открывается | `docker compose ps`, проверьте DNS и firewall (80/443) |
| 502 Bad Gateway | `docker compose logs backend frontend`, перезапуск: `docker compose restart` |
| Нет места на диске | `docker system prune -a`, удалите старые бэкапы |
| OOM / сервер зависает | Увеличьте swap или тариф RAM до 2 ГБ |
| SSL не работает | Повторите шаг 7.2, проверьте DNS |
| Админка 403 CSRF | Проверьте `CSRF_TRUSTED_ORIGINS` в `.env` |
| `search_vector does not exist` при migrate | Обновите код (`git pull`), пересоберите backend. На чистой БД достаточно `up -d --build`. Если данных нет: `docker compose down -v` и поднять заново |

---

## 14. Полезные команды

```bash
# Логи
docker compose logs -f backend

# Перезапуск одного сервиса
docker compose restart frontend

# Зайти в shell Django
docker compose exec backend python manage.py shell

# Место на диске
df -h && docker system df
```

---

## 15. Контакты и документы проекта

| Документ | Путь |
|---|---|
| Описание сайта | `docs/SITE-OPISANIE.txt` |
| Гайд админки | `docs/admin-guide.md` |
| Импорт каталога | `docs/import-guide.md` |
| После запуска | `docs/post-launch.md` |

**Старый сайт:** [ekontaktor.ru](https://www.ekontaktor.ru/) — после успешного деплоя новый сайт заменит его на том же домене.
