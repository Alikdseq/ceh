# AGENTS.md — правила и карта проекта для AI-агентов

> **Обязательный документ для любого AI-агента, начинающего работу с репозиторием `cehsite`.**  
> Прочитайте его **целиком** перед первым изменением кода.  
> Проект: официальный B2B-сайт АО «Владикавказский завод «Электроконтактор» (ekontaktor.ru).

---

## 0. Быстрый старт (60 секунд)

| Что | Где |
|-----|-----|
| Суть проекта | B2B-сайт производителя: каталог → корзина-заявка → email менеджерам |
| Монорепо | `backend/` (Django) + `frontend/` (Next.js) + `docker/` |
| Локальный запуск | `docker compose up -d --build` из корня (нужен **Docker Desktop Running**) |
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000/api/v1/ |
| Админка CMS | http://localhost:8000/manage/ |
| Полное описание для людей | [docs/SITE-OPISANIE.txt](./docs/SITE-OPISANIE.txt) |
| Техническое задание | [TZ.md](./TZ.md) |
| План реализации | [PLAN.md](./PLAN.md) |

---

## 1. Неприкосновенные правила (НАРУШАТЬ НЕЛЬЗЯ)

### 1.1. Бизнес и домен

1. **Это B2B-сайт производителя, не интернет-магазин.** Нет оплаты картой, нет личного кабинета покупателя. Есть **корзина-заявка** → коммерческое предложение → договор.
2. **Цены публичные** — из прайса завода, с НДС. Не скрывать и не выдумывать цены.
3. **Продукция: Group → Variant (SKU).** Одна карточка в каталоге = `ProductGroup`; конкретный артикул = `ProductVariant`. Не ломать эту иерархию.
4. **Язык интерфейса — русский.** Все подписи, характеристики, ошибки — для клиентов на русском. Код и комментарии — на английском (конвенция кодовой базы).
5. **Юридические страницы** (`/privacy`, `/terms`) — полные тексты с реквизитами АО «Электроконтактор». Не заменять заглушками. Источник: `frontend/src/content/legal/` и `backend/fixtures/legal/`.
6. **Не удалять «Честный знак»** и блок anti-counterfeit без явного запроса заказчика.
7. **Не возвращать «Заказать звонок»** — функционал сознательно убран; остаётся «Написать нам».

### 1.2. Архитектура

8. **Headless: frontend не ходит в БД напрямую.** Все данные — через REST API (`/api/v1/`). Server Components используют `fetchApi`, client — `fetchApiClient` / `fetchCartApi`.
9. **Не менять URL API без синхронного обновления frontend** (`frontend/src/lib/api/`).
10. **CMS-контент** (страницы about, dealers, news) — из backend API. Исключение: legal-страницы — статика во frontend (`legal-content.ts`).
11. **SEO-критичные страницы — SSR.** Каталог, карточки товаров, новости — Server Components; не переводить на чистый CSR без причины.
12. **Миграции Django — только через `makemigrations`/`migrate`.** Не править БД вручную. Не удалять миграции из git.

### 1.3. Код и качество

13. **Минимальный diff.** Менять только то, что нужно для задачи. Не рефакторить «заодно».
14. **Следовать существующим паттернам.** Перед новым компонентом — найти аналог в `frontend/src/components/`.
15. **Не добавлять зависимости** без необходимости. Стек зафиксирован в TZ §4.
16. **Не коммитить секреты:** `.env`, пароли, ключи API. Только `.env.example`.
17. **Не коммитить**, если пользователь явно не попросил.
18. **Тесты** — добавлять только если задача это требует или покрывают реальное поведение (не тривиальные assert true).
19. **TypeScript strict** — без `any` без причины. Типы в `frontend/src/lib/types.ts`.

### 1.4. UI/UX

20. **Design System Variant B** — синий `#0077AF` + терракотовый CTA `#E87A20`. См. [docs/design/DESIGN_SYSTEM.md](./docs/design/DESIGN_SYSTEM.md).
21. **shadcn/ui + Radix** — использовать готовые компоненты из `frontend/src/components/ui/`. Не писать modal/select с нуля.
22. **Плагин `tailwindcss-animate` НЕ установлен.** Не использовать классы `animate-in`, `fade-out-0`, `zoom-out-95` без проверки. Для Dialog — opacity/transition или `display:none` на `[data-state=closed]` (см. `globals.css`).
23. **Нет nested `<a>`** внутри `<a>`. ProductCard — `<article>` с отдельными ссылками на изображение и название.
24. **Fixed header** — `layout.tsx` имеет `pt-[var(--site-header-height)]`. Не ломать отступ main.
25. **Характеристики на русском** — через `specKeyLabel()`, `executionLabel()`, `productTypeLabel()` в `lib/utils.ts`.

### 1.5. Docker и окружение (Windows)

26. **Docker Desktop должен быть запущен** (`Engine running`) перед `docker compose`.
27. **Порт 3000 — один процесс.** Не запускать одновременно `npm run dev` и контейнер `frontend`.
28. **Backend на Windows:** bind-mount `./backend:/app` вызывает OOM. В `docker-compose.yml` backend работает **без** mount исходников — после изменений backend: `docker compose build backend && docker compose up -d backend`.
29. **Frontend mount** `./frontend:/app` — работает; hot reload доступен.
30. **Переменные окружения** — из `.env` в корне (копия `.env.example`).

---

## 2. Порядок изучения проекта (для нового агента)

```
1. AGENTS.md          ← вы здесь (правила + карта)
2. docs/SITE-OPISANIE.txt  ← бизнес-контекст простым языком
3. TZ.md §1–7, §11   ← функциональные требования и дизайн
4. README.md         ← запуск и URL сервисов
5. Целевые файлы     ← по задаче (см. §4)
```

**Перед задачей по каталогу** → `backend/apps/products/`, `frontend/src/components/catalog/`  
**Перед задачей по заявкам** → `backend/apps/quotes/`, `frontend/src/components/cart/`  
**Перед задачей по формам** → `backend/apps/leads/`, `frontend/src/components/leads/`  
**Перед задачей по SEO** → `backend/apps/seo/`, `frontend/src/app/sitemap.xml/`, `lib/schema.ts`

---

## 3. Карта репозитория

```
cehsite/
│
├── AGENTS.md                 ← ЭТОТ ФАЙЛ — правила для AI
├── TZ.md                     ← Полное ТЗ (802 строки)
├── PLAN.md                   ← План из 120+ шагов
├── README.md                 ← Быстрый старт
├── docker-compose.yml        ← Dev-окружение (9 сервисов)
├── .env.example              ← Шаблон переменных (не секреты!)
│
├── backend/                  ← Django 5.1 + DRF
│   ├── config/
│   │   ├── settings/         base.py, dev.py, prod.py
│   │   ├── urls.py           Корневые URL (+ admin /manage/)
│   │   ├── api_urls.py       /api/v1/ маршруты
│   │   └── celery.py         Celery app
│   ├── apps/
│   │   ├── products/         ★ Каталог: Category, ProductGroup, Variant, Spec, Search
│   │   ├── quotes/           Корзина (QuoteCart), заявки (QuoteRequest), PDF
│   │   ├── leads/            ContactLead, DealerLead, email-задачи
│   │   ├── content/          Page, NewsPost, FAQ, SiteSettings
│   │   ├── newsletter/       Подписчики, кампании, double opt-in
│   │   ├── docs/             Document (паспорта, чертежи)
│   │   ├── seo/              Redirect, sitemap, generate_sitemap
│   │   └── users/            setup_groups, staff roles
│   ├── fixtures/             seed_content.json, legal/*.html
│   ├── templates/            Email и PDF (quotes/, leads/, newsletter/)
│   └── manage.py
│
├── frontend/                 ← Next.js 16 App Router
│   ├── src/app/              ★ Страницы (file-based routing)
│   │   ├── page.tsx          Главная
│   │   ├── catalog/          Каталог + [...slug] catch-all
│   │   ├── cart/             Корзина-заявка
│   │   ├── compare/          Сравнение
│   │   ├── search/           Поиск
│   │   ├── privacy/ terms/   Legal (статика)
│   │   └── layout.tsx        Root layout, header offset
│   ├── src/components/
│   │   ├── ui/               shadcn: button, dialog, select, sheet...
│   │   ├── catalog/          ProductCard, CatalogFilters, CategoryCard
│   │   ├── product/          ProductConfigurator, ProductTabs, Gallery
│   │   ├── cart/             CartPageClient, QuoteForm
│   │   ├── leads/            ContactLeadDialog, DealerForm
│   │   └── layout/           Header, Footer, Breadcrumbs
│   ├── src/lib/
│   │   ├── api/              ★ API-клиент по доменам (client.ts — база)
│   │   ├── types.ts          TypeScript-интерфейсы API
│   │   ├── catalog-params.ts URL query для фильтров
│   │   ├── utils.ts          specKeyLabel, formatPrice, executionLabel
│   │   └── legal-content.ts  Privacy/Terms HTML
│   └── AGENTS.md             Next.js 16 breaking changes notice
│
├── docker/
│   ├── backend/Dockerfile
│   └── frontend/Dockerfile
├── data/                     Импорт: pricelist.csv, categories.yaml, PDF
├── docs/
│   ├── SITE-OPISANIE.txt     Полное описание для заказчика
│   ├── design/               DESIGN_TZ, DESIGN_SYSTEM, wireframes
│   ├── admin-guide.md
│   └── import-guide.md
└── nginx/                    Reverse proxy (prod)
```

---

## 4. Архитектура (как всё связано)

```
┌──────────────┐   REST JSON    ┌──────────────┐
│   Next.js    │ ◄────────────► │   Django     │
│  :3000       │  /api/v1/    │  :8000       │
│  SSR + RSC   │                │  DRF + Admin │
└──────────────┘                └──────┬───────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    ▼                  ▼                  ▼
              PostgreSQL 16       Redis 7            MinIO (S3)
              (catalog, CMS)   (cache, Celery)      (files, prod)
                                       │
                                       ▼
                                  Celery Worker
                              (email, PDF, sitemap)
```

### Поток заявки (критический business flow)

```
ProductConfigurator → addToCart (localStorage + API session)
    → /cart/ → QuoteForm → POST /api/v1/quotes/
    → QuoteRequest в БД → Celery: email менеджерам + PDF клиенту
    → /order/success/
```

### Поток каталога

```
/catalog/ → CategoryList API → CategoryCard grid
/catalog/{cat}/ → ProductGroupList + CatalogFilters (URL query)
/catalog/{cat}/{product}/ → ProductGroupDetail + ProductConfigurator
    → variant slug в ?variant= → ProductVariant
```

---

## 5. Backend: ключевые модели

| Модель | App | Назначение |
|--------|-----|------------|
| `Category` (MPTT) | products | Дерево категорий |
| `ProductGroup` | products | Страница товара в каталоге |
| `ProductVariant` | products | SKU: артикул, цена, исполнение, катушка |
| `ProductSpec` | products | Характеристики для фильтров и таблицы |
| `QuoteCart` / `QuoteCartItem` | quotes | Сессионная корзина |
| `QuoteRequest` | quotes | Заявка с номером ЗК-YYYY-NNNNN |
| `ContactLead` | leads | Форма «Написать нам» |
| `Page` / `NewsPost` / `FAQItem` | content | CMS |
| `SiteSettings` | content | Singleton: телефоны, email, адрес |
| `NewsletterSubscriber` | newsletter | Double opt-in рассылка |
| `Redirect` | seo | 301 с old URL |
| `Document` | docs | PDF, DWG, паспорта |

### Management commands (импорт данных)

```bash
docker compose exec backend python manage.py import_categories /data/categories.yaml
docker compose exec backend python manage.py import_pricelist /data/pricelist.csv
docker compose exec backend python manage.py import_catalog_text /data/тексткаталога.txt
docker compose exec backend python manage.py rebuild_search_index
docker compose exec backend python manage.py loaddata fixtures/seed_content.json
docker compose exec backend python manage.py setup_groups
```

### API base: `/api/v1/`

| Endpoint | Метод | Описание |
|----------|-------|----------|
| `/settings/` | GET | SiteSettings |
| `/categories/` | GET | Дерево категорий |
| `/products/` | GET | Список (+ фильтры) |
| `/products/{slug}/` | GET | Карточка группы |
| `/compare/?ids=1,2,3` | GET | Данные сравнения |
| `/search/?q=` | GET | Полнотекстовый поиск |
| `/search/suggest/?q=` | GET | Автодополнение |
| `/cart/` | GET/POST/PATCH/DELETE | Корзина |
| `/quotes/` | POST | Отправка заявки |
| `/leads/contact/` | POST | Обратная связь |
| `/pages/{slug}/` | GET | CMS-страница |
| `/news/` | GET | Новости |

Swagger: http://localhost:8000/api/docs/

---

## 6. Frontend: конвенции

### 6.1. Структура компонентов

- **`page.tsx`** — Server Component по умолчанию; `async`, fetch API, metadata.
- **`"use client"`** — только для интерактива: формы, фильтры, cart, dialog.
- **Не передавать функции** из Server Component в Client Component как props.
- **API вызовы:** server → `fetchApi` из `@/lib/api/client`; client → `fetchApiClient`.

### 6.2. Стили

- Tailwind CSS 4, токены в `globals.css` (`:root` + `@theme inline`).
- Container: класс `container-page` (max 1280px).
- Секции: `section-py`.
- Шрифты: Manrope (display), Inter (body) — в `layout.tsx`.

### 6.3. Каталог — URL-параметры

Определены в `lib/catalog-params.ts`:

```
?current=400&coil=220&poles=3&execution=B&product_type=KT&series=6000
&ordering=nominal_current_a&page_size=24&view=grid&page=1
```

Фильтры **сохраняются в URL** — не ломать shareable links.

### 6.4. Routing каталога

- `catalog/[...slug]/page.tsx` — catch-all: категория ИЛИ товар (3+ сегментов).
- `tryGetProduct(lastSegment)` — проверка product slug до CategoryListing.
- Breadcrumbs: `lib/categories.ts` → `buildCategoryBreadcrumbs`.

### 6.5. Известные паттерны и ловушки

| Проблема | Решение |
|----------|---------|
| Dialog не закрывается | `DialogPrimitive.Close` + conditional render `{open && <DialogContent>}` в LeadDialogs |
| Select фильтра не закрывается | `setOpen(false)` до navigate; fix viewport в `ui/select.tsx` |
| Nested links hydration error | ProductCard: `<article>`, не `<Link>` вокруг всей карточки |
| API unreachable на dev | Backend не запущен → `docker compose up -d db redis backend` |
| Legal pages пустые | Контент в `frontend/src/content/legal/`, не только CMS |

---

## 7. Команды разработчика

### Docker (рекомендуется)

```powershell
cd C:\cehsite
docker compose up -d --build          # всё
docker compose up -d db redis backend # только API (frontend локально)
docker compose logs -f backend        # логи
docker compose ps                     # статус
docker compose build backend          # после изменений backend-кода
```

### Frontend локально

```powershell
cd frontend
npm install
npm run dev        # :3000 — только если Docker frontend выключен
npm run build      # проверка перед PR
npm run lint
npm run test       # vitest
npm run test:e2e   # playwright
```

### Backend тесты

```powershell
docker compose exec backend pytest
docker compose exec backend python manage.py test
```

---

## 8. Роли админки

| Группа | Права |
|--------|-------|
| SuperAdmin | Полный доступ |
| ContentManager | Контент + каталог |
| SalesManager | Заявки + лиды |
| ReadOnly | Только просмотр |

Создание: `python manage.py setup_groups` + `createsuperuser`

---

## 9. Чеклист агента перед сдачей задачи

- [ ] Прочитал AGENTS.md и затронутые модули
- [ ] Diff минимален, без unrelated changes
- [ ] Русский UI для пользовательских текстов
- [ ] Не сломан SSR/SEO на затронутых страницах
- [ ] Dialog/Select/Forms работают (если трогал ui/)
- [ ] `npm run build` проходит (если менял frontend)
- [ ] Backend тесты проходят (если менял backend)
- [ ] Нет секретов в diff
- [ ] Не создан commit без запроса пользователя

---

## 10. Чего НЕ делать (anti-patterns)

| ❌ Нельзя | ✅ Вместо этого |
|----------|----------------|
| E-commerce с оплатой | Корзина-заявка |
| Хардкод цен в frontend | API / import_pricelist |
| `fetch` напрямую с разными URL | `lib/api/client.ts` |
| Новый UI-kit | shadcn/ui в `components/ui/` |
| Удалять миграции | Новая migration |
| `tailwindcss-animate` классы | opacity transition / globals.css fix |
| Force push в main | Обычный push, PR |
| Править `.env` в git | `.env.example` |
| Nested `<a>` | `<article>` + отдельные links |
| Callback «Заказать звонок» | ContactLeadDialog «Написать» |

---

## 11. Документы по темам

| Тема | Файл |
|------|------|
| Бизнес-описание | [docs/SITE-OPISANIE.txt](./docs/SITE-OPISANIE.txt) |
| Функциональные требования | [TZ.md](./TZ.md) |
| План шагов | [PLAN.md](./PLAN.md) |
| Дизайн (полный) | [docs/design/DESIGN_TZ.md](./docs/design/DESIGN_TZ.md) |
| Design tokens | [docs/design/DESIGN_SYSTEM.md](./docs/design/DESIGN_SYSTEM.md) |
| Импорт каталога | [docs/import-guide.md](./docs/import-guide.md) |
| Админка | [docs/admin-guide.md](./docs/admin-guide.md) |
| UAT | [docs/UAT-CHECKLIST.md](./docs/UAT-CHECKLIST.md) |
| Хостинг prod | [docs/infrastructure/HOSTING.md](./docs/infrastructure/HOSTING.md) |
| Docker локально | [LOCAL-RUN.txt](./LOCAL-RUN.txt) |
| Данные заказчика | [data/CLIENT_INPUT.md](./data/CLIENT_INPUT.md) |

---

## 12. Контекст заказчика (кратко)

- **Заказчик:** АО «Владикавказский завод «Электроконтактор», с 1956 г.
- **Домен:** ekontaktor.ru
- **Email заявок:** info@ekontaktor.ru, elkonreal@yandex.ru
- **Продукция:** контакторы КТ/КТП/КТЭ, выключатели, кулачковые элементы, аксессуары
- **УТП:** прямой производитель, Честный знак, российские комплектующие, полная документация на сайте

---

## 13. Версии стека (актуально на 07.2026)

| Компонент | Версия |
|-----------|--------|
| Python | 3.12 |
| Django | 5.1 |
| DRF | 3.15+ |
| PostgreSQL | 16 |
| Redis | 7 |
| Next.js | 16.x |
| React | 19 |
| TypeScript | 5 |
| Tailwind CSS | 4 |
| Node | 20+ |

> **Next.js 16:** API отличается от training data. См. `frontend/AGENTS.md` и `node_modules/next/dist/docs/`.

---

*Последнее обновление: 03.07.2026. При изменении архитектуры или правил — обновляйте этот файл в том же PR.*
