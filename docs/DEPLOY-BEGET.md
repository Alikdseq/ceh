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
root@gpustejida:/opt/ekontaktor# ls -la .env

ls: cannot access '.env': No such file or directory

root@gpustejida:/opt/ekontaktor# ls -la /root/ekontaktor.env.bak

-rw-r--r-- 1 root root 789 Jul 10 23:17 /root/ekontaktor.env.bak

Бэкап есть — восстанови .env и запускай:

cd /opt/ekontaktor
cp /root/ekontaktor.env.bak .env
chmod 600 .env
# проверка, что пароль задан (значение не покажет sed — только имена)
grep -E '^(POSTGRES_PASSWORD|DATABASE_URL|SECRET_KEY)=' .env | sed 's/=.*/=***/'
Если POSTGRES_PASSWORD пустой или строки нет — допиши вручную:

nano .env
Должно быть примерно так:

POSTGRES_PASSWORD=ваш_пароль
DATABASE_URL=postgres://ekontaktor:ваш_пароль@db:5432/ekontaktor
SECRET_KEY=длинная_случайная_строка
Запуск:

docker compose -f docker-compose.prod.yml -f docker-compose.prod.beget.yml up -d --build
docker compose -f docker-compose.prod.yml -f docker-compose.prod.beget.yml logs --tail=50 backend
Если backend пишет password authentication failed — пароль в .env не совпадает с тем, с которым уже создана БД. Тогда либо верни старый пароль в .env, либо при пустой БД:

docker compose -f docker-compose.prod.yml -f docker-compose.prod.beget.yml down
docker volume rm ekontaktor_postgres_data
docker compose -f docker-compose.prod.yml -f docker-compose.prod.beget.yml up -d --build
Пришли последние 30 строк logs backend, если что-то ещё упадёт.

[+] Building 275.1s (23/27)

 => [internal] load local bake definitions                                                                         0.0s

 => => reading from stdin 1.70kB                                                                                   0.0s

 => [backend internal] load build definition from Dockerfile.prod                                                  0.0s

 => => transferring dockerfile: 722B                                                                               0.0s

 => [frontend internal] load build definition from Dockerfile.prod                                                 0.0s

 => => transferring dockerfile: 576B                                                                               0.0s

 => [celery internal] load metadata for mirror.gcr.io/library/python:3.12-slim                                     1.5s

 => [frontend internal] load metadata for docker.io/library/node:20-alpine                                         1.1s

 => [frontend internal] load .dockerignore                                                                         0.0s

 => => transferring context: 178B                                                                                  0.0s

 => [frontend builder 1/6] FROM docker.io/library/node:20-alpine@sha256:fb4cd12c85ee03686f6af5362a0b0d56d50c58a04  0.0s

 => => resolve docker.io/library/node:20-alpine@sha256:fb4cd12c85ee03686f6af5362a0b0d56d50c58a04632e6c0fb8363f609  0.0s

 => [frontend internal] load build context                                                                         2.6s

 => => transferring context: 113.97MB                                                                              2.6s

 => [celery internal] load .dockerignore                                                                           0.1s

 => => transferring context: 627B                                                                                  0.0s

 => [celery 1/6] FROM mirror.gcr.io/library/python:3.12-slim@sha256:423ed6ab25b1921a477529254bfeeabf5855151dc2c31  0.7s

 => => resolve mirror.gcr.io/library/python:3.12-slim@sha256:423ed6ab25b1921a477529254bfeeabf5855151dc2c3141699a1  0.6s

 => [celery internal] load build context                                                                           0.3s

 => => transferring context: 459.21kB                                                                              0.2s

 => CACHED [celery 2/6] WORKDIR /app                                                                               0.0s

 => CACHED [celery 3/6] RUN apt-get update && apt-get install -y --no-install-recommends     libpq-dev gcc     li  0.0s

 => CACHED [celery 4/6] COPY backend/requirements/base.txt /requirements/base.txt                                  0.1s

 => [celery 5/6] RUN pip install --no-cache-dir -r /requirements/base.txt                                        137.1s

 => CACHED [frontend builder 2/6] WORKDIR /app                                                                     0.0s

 => CACHED [frontend builder 3/6] COPY package*.json ./                                                            0.0s

 => CACHED [frontend builder 4/6] RUN npm ci                                                                       0.0s

 => CACHED [frontend builder 5/6] COPY . .                                                                         0.0s

 => CANCELED [frontend builder 6/6] RUN npm run build                                                            268.3s

 => [celery 6/6] COPY backend/ /app/                                                                               2.9s

 => ERROR [backend] exporting to image                                                                           123.4s

 => => exporting layers                                                                                          111.6s

 => => exporting manifest sha256:7fd5f0470796fdd8c364a4d01cc5d501b288d9dc272ab17f9eda7b1c0209b6eb                  0.3s

 => => exporting config sha256:5f582f69f271c649bb7390b14744eed2fedc733ecc5fbf9c22001c9be917636c                    0.4s

 => => exporting attestation manifest sha256:f018ee12eaf1af0517a602bb91f41bad28760372634f7ba6ddb47a90ba9f2025      0.5s

 => => exporting manifest list sha256:e1b2c4d95593dd15c74abcc07d4682ee223f86aa5b312f32992b8e23e297d7d7             0.3s

 => => naming to docker.io/library/ekontaktor-backend:latest                                                       0.2s

 => => unpacking to docker.io/library/ekontaktor-backend:latest                                                    9.7s

 => ERROR [celery] exporting to image                                                                            123.4s

 => => exporting layers                                                                                          111.6s

 => => exporting manifest sha256:d491871cb34f283b23f1802ecdc53f3fd0e81d76f55f58ed1340f35097344ad8                  0.3s

 => => exporting config sha256:78e88db1f5e43764d989305a2306d61961590098aaa8e886c2726113bcd6036f                    0.4s

 => => exporting attestation manifest sha256:cded8ed03a5080eded8ddcf334c2281d69bfa261481d4f85786b05db259893b4      0.4s

 => => exporting manifest list sha256:d1114f8be8d4c77660528a1bba5c11b6c15f64cba5260c87ce70bafb082088ba             0.2s

 => => naming to docker.io/library/ekontaktor-celery:latest                                                        0.2s

 => => unpacking to docker.io/library/ekontaktor-celery:latest                                                     9.7s

------

 > [backend] exporting to image:

------

------

 > [celery] exporting to image:

------

[+] up 0/3

 ⠙ Image ekontaktor-frontend Building                                                                             275.2s

 ⠙ Image ekontaktor-celery   Building                                                                             275.2s

 ⠙ Image ekontaktor-backend  Building                                                                             275.2s

target celery: failed to solve: failed to extract layer sha256:e5806445cd3f978da08c2ffb034bdb5639ce3d693bc463f806dc889a910ca9fb: write /var/lib/containerd/io.containerd.snapshotter.v1.overlayfs/snapshots/136/fs/usr/libexec/gcc/x86_64-linux-gnu/14/cc1: no space left on device

На диске VPS закончилось место (no space left on device). Сборка backend/celery/frontend параллельно съела весь объём.

1. Посмотри, что занято
df -h
docker system df
du -sh /opt/* /var/lib/docker 2>/dev/null
2. Освободи место (безопасно для Docker)
# остановить контейнеры
cd /opt/ekontaktor
docker compose -f docker-compose.prod.yml -f docker-compose.prod.beget.yml down
# удалить мусор Docker: кэш сборки, неиспользуемые образы
docker builder prune -af
docker system prune -af --volumes
# если есть старая папка после git clone
rm -rf /opt/ekontaktor.old
# системный кэш (опционально)
apt-get clean
journalctl --vacuum-size=50M
Снова проверь:

df -h
Нужно минимум 3–4 ГБ свободно для первой сборки (frontend + backend).

3. Собирай по очереди, не всё сразу
cd /opt/ekontaktor
# сначала backend (celery использует тот же образ)
docker compose -f docker-compose.prod.yml -f docker-compose.prod.beget.yml build backend
# потом frontend отдельно
docker compose -f docker-compose.prod.yml -f docker-compose.prod.beget.yml build frontend
# запуск без пересборки
docker compose -f docker-compose.prod.yml -f docker-compose.prod.beget.yml up -d
4. Если места всё равно мало
Временно подними только backend + db + redis + nginx (без frontend):

docker compose -f docker-compose.prod.yml -f docker-compose.prod.beget.yml up -d db redis backend nginx
docker compose -f docker-compose.prod.yml -f docker-compose.prod.beget.yml logs --tail=30 backend
Проверь API: curl -s http://127.0.0.1:8000/api/v1/categories/ | head

Frontend соберёшь позже, когда освободишь диск.

5. Если диск совсем маленький (< 10 ГБ)
В панели Beget увеличь диск на VPS или выбери тариф с большим SSD. На 1 ГБ RAM + маленький диск первая сборка Next.js + Python часто не влезает.

Пришли вывод:

df -h
docker system df
— подскажу, хватит ли места или что ещё удалить.

root@gpustejida:/opt/ekontaktor# df -h

Filesystem      Size  Used Avail Use% Mounted on

tmpfs            97M  1.1M   96M   2% /run

/dev/vda1       8.7G  7.5G  1.3G  86% /

tmpfs           481M     0  481M   0% /dev/shm

tmpfs           5.0M     0  5.0M   0% /run/lock

/dev/vda16      881M  117M  703M  15% /boot

/dev/vda15      105M  6.2M   99M   6% /boot/efi

tmpfs            97M  8.0K   97M   1% /run/user/0

root@gpustejida:/opt/ekontaktor# docker system df

TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE

Images          7         0         2.402GB   1.929GB (80%)

Containers      0         0         0B        0B

Local Volumes   6         0         4.243kB   4.243kB (100%)

Build Cache     18        18        1.64GB    0B

root@gpustejida:/opt/ekontaktor# du -sh /opt/* /var/lib/docker 2>/dev/null

12K     /opt/containerd

993M    /opt/ekontaktor

11M     /var/lib/docker

Диск почти полный: 1.3 ГБ свободно, а Docker держит ~4 ГБ (образы + кэш сборки). Для первой сборки этого мало.

1. Освободи Docker (~3.5 ГБ)

cd /opt/ekontaktor
docker compose -f docker-compose.prod.yml -f docker-compose.prod.beget.yml down 2>/dev/null
docker builder prune -af
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
# Категории (в Docker папка data/ с хоста смонтирована как /data/)
docker compose -f docker-compose.prod.yml -f docker-compose.prod.beget.yml exec backend python manage.py import_categories /data/categories.yaml

# Разделение карточек по исполнению Б/БС/С (после обновления каталога)
docker compose -f docker-compose.prod.yml -f docker-compose.prod.beget.yml exec backend python manage.py split_products_by_execution

# Каталог из текста (если есть файл)
docker compose -f docker-compose.prod.yml -f docker-compose.prod.beget.yml exec backend python manage.py import_catalog_text /data/тексткаталога.txt

# Прайс-лист
docker compose -f docker-compose.prod.yml -f docker-compose.prod.beget.yml exec backend python manage.py import_pricelist /data/pricelist.csv

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
