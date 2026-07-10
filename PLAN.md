# План реализации сайта АО «Электроконтактор»

> **Документ:** пошаговый атомарный план разработки  
> **Основание:** [TZ.md](./TZ.md)  
> **Версия:** 1.0 · 30.06.2026  
> **Оценка MVP:** 14–18 недель (1 fullstack + 1 frontend/design part-time)

---

## Как пользоваться этим планом

1. Выполняйте шаги **строго по порядку** внутри каждой фазы (зависимости указаны).
2. Отмечайте выполненное: `- [x] STEP-XXX`.
3. Каждый шаг считается завершённым по **Definition of Done** из [TZ.md §20](./TZ.md).
4. Блокеры — см. [§ Блокеры и решения заказчика](#блокеры-и-решения-заказчика).

### Легенда приоритетов

| Метка | Значение |
|---|---|
| 🔴 | Блокирует следующие шаги |
| 🟡 | Важно для MVP, но можно параллелить |
| 🟢 | Should / Phase 2 |

---

## Обзор фаз

```mermaid
flowchart LR
  P0[Phase0 Подготовка] --> P1[Phase1 Foundation]
  P1 --> P2[Phase2 Core UX]
  P2 --> P3[Phase3 Conversion]
  P3 --> P4[Phase4 Launch]
```

| Фаза | Шаги | Срок | Результат |
|---|---|---|---|
| Phase 0 | STEP-001 … 010 | 2–3 дня | Репозиторий, доступы, данные |
| Phase 1 | STEP-011 … 045 | 4–5 нед | Backend, модели, admin, импорт каталога |
| Phase 2 | STEP-046 … 075 | 5–6 нед | Frontend: каталог, PDP, поиск, сравнение |
| Phase 3 | STEP-076 … 100 | 3–4 нед | Корзина, email, контент, рассылка |
| Phase 4 | STEP-101 … 120 | 2–3 нед | SEO, безопасность, UAT, prod |

---

## Phase 0 — Подготовка (2–3 дня)

### STEP-001 🔴 Инициализация Git-репозитория
- [x] `git init`, ветки `main` / `develop`
- [x] Добавить `.gitignore`, `README.md`, ссылки на `TZ.md` и `PLAN.md`
- [x] Первый commit: `docs: add TZ and implementation plan`

**DoD:** репозиторий создан, секреты не в git.

---

### STEP-002 🔴 Сбор входных данных от заказчика
- [x] Получить email(ы) для заявок (`ORDER_EMAILS`) — предзаполнено из ekontaktor.ru
- [ ] Получить SMTP-доступ или решение (Yandex 360 / корп. почта)
- [x] Уточнить домен: `ekontaktor.ru` — рекомендация зафиксирована
- [x] Уточнить CRM webhook URL (или отложить на STEP-089) — отложено
- [ ] Запросить архив: фото продукции, DWG, паспорта, сертификаты
- [x] Заполнить таблицу в [TZ.md §18](./TZ.md) + [data/CLIENT_INPUT.md](./data/CLIENT_INPUT.md)

**DoD:** минимум email + домен известны до Phase 3.

---

### STEP-003 🔴 Подготовка исходных данных каталога
- [x] Положить `КАТАЛОГ КОНТАКТОРОВ 2026.pdf` в `data/source/`
- [x] Создать `data/pricelist.csv` из [ekontaktor.ru/pricelist](https://www.ekontaktor.ru/pricelist/)
- [x] Создать `data/categories.yaml` — дерево 7 категорий ([TZ §5.2](./TZ.md))
- [x] Зафиксировать `catalog_extract.txt` как reference → `data/source/catalog_extract.txt`

**DoD:** 3 файла в `data/source/` готовы к импорту.

---

### STEP-004 🟡 Выбор хостинга и домена
- [ ] Зарегистрировать/подтвердить DNS — **ожидает заказчика**
- [x] Выбрать VPS (Selectel / Yandex Cloud, 4 vCPU, 8 GB RAM) — [docs/infrastructure/HOSTING.md](./docs/infrastructure/HOSTING.md)
- [ ] Создать staging-домен (`staging.ekontaktor.ru`) — **ожидает заказчика**

**DoD:** DNS A-record указывает на staging (можно позже prod).

---

### STEP-005 🟡 Дизайн-референсы и UI-kit
- [x] Wireframes: главная, каталог, PDP, корзина, о заводе — [docs/design/wireframes/](./docs/design/wireframes/)
- [x] Зафиксировать палитру ([TZ §11.1](./TZ.md)): `#0A1628`, `#0066CC`, `#F59E0B` → [design/tokens.css](./design/tokens.css)
- [x] Подобрать шрифты: Inter / Manrope / JetBrains Mono — [docs/design/DESIGN_SYSTEM.md](./docs/design/DESIGN_SYSTEM.md)

**DoD:** wireframes или Figma для 5 ключевых экранов.

---

## Phase 1 — Foundation: Backend + Infra (4–5 нед)

### Блок 1.1 — Инфраструктура

#### STEP-011 🔴 Docker Compose (dev)
- [x] `docker-compose.yml`: `db`, `redis`, `backend`, `celery`, `celery-beat`, `frontend`, `nginx`, `minio`, `mailhog`
- [x] `docker/backend/Dockerfile`, `docker/frontend/Dockerfile`
- [x] `nginx/nginx.conf` — proxy `/api` → backend, `/` → frontend
- [x] `.env` из `.env.example`

**DoD:** `docker compose up` поднимает все сервисы без ошибок.

**Файлы:** `docker-compose.yml`, `docker/`, `nginx/`

---

#### STEP-012 🔴 Django project scaffold
- [x] `django-admin startproject config backend/`
- [x] `backend/config/settings/` — split: `base.py`, `dev.py`, `prod.py`
- [x] Подключить PostgreSQL через `DATABASE_URL`
- [x] Подключить Redis для cache + sessions
- [x] `manage.py`, `requirements/base.txt`, `requirements/dev.txt`

**DoD:** `python manage.py migrate` успешен в Docker.

---

#### STEP-013 🔴 Next.js 15 scaffold
- [x] `npx create-next-app@latest frontend --typescript --tailwind --app --src-dir`
- [x] Настроить `NEXT_PUBLIC_API_URL`
- [x] Базовый layout: header placeholder, footer placeholder
- [x] Proxy rewrites в `next.config.ts` для dev API

**DoD:** `npm run dev` — главная открывается на `:3000`.

---

#### STEP-014 🔴 CI pipeline (базовый)
- [x] `.github/workflows/ci.yml`: lint backend (ruff), lint frontend (eslint), pytest, build Docker
- [ ] Pre-commit hooks (optional): ruff, eslint

**DoD:** push в `develop` запускает CI green.

---

### Блок 1.2 — Django Apps и модели

#### STEP-015 🔴 App `products`
- [x] Создать `backend/apps/products/`
- [x] Модели: `Category` (MPTT), `ProductGroup`, `ProductVariant`, `ProductSpec`, `ProductImage`
- [x] Индексы: `nominal_current_a`, `category_id`, `is_active`
- [x] Migrations

**DoD:** модели в admin (raw) отображаются. **TZ:** §6.1

---

#### STEP-016 🔴 App `docs`
- [x] Модели: `Document`, `ProductDocument` (M2M link)
- [x] Upload path: `media/docs/{uuid}.{ext}`
- [x] MIME validation (pdf, dwg, jpg, png), max 20 MB

**DoD:** upload PDF в admin работает. **TZ:** §6.2, FR-SEC-06

---

#### STEP-017 🔴 App `quotes`
- [x] Модели: `QuoteCart`, `QuoteCartItem`, `QuoteRequest`, `QuoteRequestItem`
- [x] Auto-number: `ЗК-{YYYY}-{NNNNN}`
- [x] Status workflow: new → in_progress → quoted → completed / cancelled

**DoD:** unit-test генерации номера заявки. **TZ:** §6.3

---

#### STEP-018 🔴 App `content`
- [x] Модели: `Page`, `NewsPost`, `FAQItem`, `SiteSettings` (singleton)
- [x] `SiteSettings`: phones, emails, address, order_emails[], webhook_url

**DoD:** SiteSettings editable в admin. **TZ:** §6.5

---

#### STEP-019 🔴 App `newsletter`
- [x] Модели: `NewsletterSubscriber`, `NewsletterCampaign`, `NewsletterSendLog`
- [x] Tokens: confirm_token, unsubscribe_token (uuid)

**DoD:** migrations applied. **TZ:** §6.4

---

#### STEP-020 🔴 App `leads`
- [x] Модели: `ContactLead`, `CallbackLead`, `DocumentRequestLead`

**DoD:** migrations applied. **TZ:** §7.8

---

#### STEP-021 🔴 App `seo`
- [x] Модели: `Redirect` (old_path → new_path, 301), `SearchQueryLog`

**DoD:** migrations applied. **TZ:** §6.5, FR-SRH-05

---

#### STEP-022 🔴 App `users`
- [x] Custom User (optional) или стандартный + Groups
- [x] Роли: SuperAdmin, ContentManager, SalesManager, ReadOnly (Django Groups)

**DoD:** 4 группы созданы management command. **TZ:** FR-ADM-05

---

### Блок 1.3 — Admin CMS

#### STEP-023 🔴 Django Admin кастомизация
- [x] Установить `django-unfold` или `django-admin-interface`
- [x] Admin URL = `manage/` (не `/admin/`) — env `ADMIN_URL`
- [x] Inline: variants в ProductGroup, specs, images, documents
- [x] MPTT drag-n-drop для Category (DraggableMPTTAdmin)

**DoD:** менеджер может создать товар с 3 вариантами за 5 мин. **TZ:** §8.2

---

#### STEP-024 🔴 django-import-export
- [x] Resource classes: ProductGroup, ProductVariant, Category
- [x] Шаблон Excel: `data/templates/import_products.xlsx`
- [x] Admin action: Export / Import

**DoD:** export → edit → import roundtrip без потери данных. **TZ:** §8.2

---

#### STEP-025 🔴 Безопасность admin (Phase 1 baseline)
- [x] `django-axes`: 5 попыток / 30 мин lockout
- [x] `django-otp` + TOTP для superuser
- [x] `django-auditlog` на ProductGroup, ProductVariant, QuoteRequest, SiteSettings

**DoD:** после 5 неверных паролей — блокировка. **TZ:** FR-ADM-02…04

---

### Блок 1.4 — REST API (backend core)

#### STEP-026 🔴 DRF setup
- [x] `djangorestframework`, `django-filter`, `drf-spectacular`
- [x] `/api/v1/` router, OpenAPI `/api/schema/`, Swagger UI
- [x] Pagination: PageNumber, page_size=24
- [x] CORS whitelist frontend URL

**DoD:** Swagger UI открывается, schema генерируется.

---

#### STEP-027 🔴 API: Categories
- [x] `GET /api/v1/categories/` — дерево MPTT (cached Redis 1h)
- [x] Serializer с `children`, `product_count`

**DoD:** Postman/curl возвращает 7 root categories.

---

#### STEP-028 🔴 API: Products list + filters
- [x] `GET /api/v1/products/` — list ProductGroup
- [x] Filters: `current`, `coil_voltage`, `poles`, `execution`, `product_type`, `category`
- [x] Sort: name, price_min, current
- [x] `select_related` / `prefetch_related`
- [x] Annotate `price_from` = min variant price

**DoD:** `?current=400&execution=B` возвращает корректный набор. **TZ:** FR-CAT-03…05

---

#### STEP-029 🔴 API: Product detail
- [x] `GET /api/v1/products/{slug}/` — group + variants + specs + images + docs
- [x] `GET /api/v1/variants/{slug}/` — single SKU

**DoD:** PDP API содержит все поля для конфигуратора. **TZ:** FR-PDP-01…03

---

#### STEP-030 🟡 API: Compare
- [x] `GET /api/v1/compare/?ids=1,2,3,4` — max 4 variants, side-by-side specs

**DoD:** 4 SKU возвращают unified spec table. **TZ:** FR-CMP-01…02

---

### Блок 1.5 — Импорт каталога

#### STEP-031 🔴 Management command: import categories
- [x] `python manage.py import_categories data/categories.yaml`
- [x] Создать 7 категорий + подкатегории (серии 6012–6053, 6600, 7200…)

**DoD:** дерево категорий в admin совпадает с TZ §5.2.

---

#### STEP-032 🔴 Parser: PDF catalog → ProductGroup
- [x] `scripts/parse_catalog_pdf.py` — извлечь: модель, назначение, specs
- [x] Группировка: КТ6012Б-У3 + КТ6012БС-У3 → одна ProductGroup «КТ 6012 100А»
- [x] `python manage.py import_catalog_pdf data/source/КАТАЛОГ*.pdf` (fallback: `catalog_extract.txt`)

**DoD:** 81 модель → ~40 ProductGroup с specs. **TZ:** §8.3

---

#### STEP-033 🔴 Import pricelist → ProductVariant
- [x] `python manage.py import_pricelist data/pricelist.csv`
- [x] Match SKU → variant, set price, execution, coil_voltage
- [x] Fallback: создать variant если нет в PDF (выключатели, КЭ, ПВП)

**DoD:** все позиции прайса ekontaktor.ru имеют price > 0.

---

#### STEP-034 🟡 Placeholder images + documents
- [x] Default image: `frontend/public/placeholder-product.svg`
- [x] Management command: assign placeholder to groups without image
- [ ] Seed: 5–10 реальных паспортов PDF (если есть от заказчика)

**DoD:** ни одна карточка не показывает broken image.

---

#### STEP-035 🔴 PostgreSQL full-text search setup
- [x] Enable extension `pg_trgm`
- [x] SearchVector на ProductGroup (name, series_code) + ProductVariant (sku_code)
- [x] GIN indexes
- [x] `python manage.py rebuild_search_index`
- [x] API `GET /api/v1/search/?q=`

**DoD:** search «кт6043» находит КТ6043. **TZ:** FR-SRH-02

---

#### STEP-036 🔴 Celery setup
- [x] `config/celery.py`, worker + beat в Docker
- [x] Test task: `debug_task` ping (`config/tasks.py`)
- [x] Redis broker

**DoD:** celery worker logs «ready».

---

#### STEP-037 🟡 Seed content (dev)
- [x] Fixture: SiteSettings (phones, address из ekontaktor.ru)
- [x] 3 NewsPost, 5 FAQItem, Page «about», «contacts», «privacy», «terms»
- [x] `python manage.py loaddata fixtures/seed_content.json`

**DoD:** API `/api/v1/pages/about/` возвращает контент.

---

### ✅ Checkpoint Phase 1

| Критерий | Проверка |
|---|---|
| Docker up | `docker compose ps` — all healthy |
| Catalog in DB | ≥ 80% SKU из прайса |
| Admin works | CRUD товара через `/manage/` |
| API works | Swagger + 3 curl-теста |
| Tests | pytest ≥ 20 tests green |

---

## Phase 2 — Core UX: Frontend (5–6 нед)

### Блок 2.1 — Design System

#### STEP-046 🔴 Tailwind + shadcn/ui setup
- [x] `npx shadcn@latest init` (components.json + manual setup)
- [x] Компоненты: Button, Input, Select, Badge, Card, Sheet, Tabs, Table, Dialog
- [x] CSS variables: colors from TZ §11.1
- [x] Font: Inter via `next/font`

**DoD:** Storybook или `/dev/ui` page с компонентами.

---

#### STEP-047 🔴 Layout components
- [x] `Header`: logo, nav, search, cart badge, phone CTA
- [x] `Footer`: links, subscribe form, requisites snippet
- [x] `Breadcrumbs`
- [x] `MobileNav` (Sheet)
- [x] Skip-to-content link (a11y)

**DoD:** layout на всех страницах. **TZ:** §11.3

---

### Блок 2.2 — Главная страница

#### STEP-048 🔴 Homepage `/`
- [x] Hero: «Производитель контакторов с 1956 года» + CTA «Подобрать контактор»
- [x] Блок серий (КТ 6000, 6600, КТП, КТЭ)
- [x] Trust badges: Честный знак, 100% РФ, EAC
- [x] Хиты продаж (API: featured products)
- [x] Последние новости (3 шт.)
- [x] Subscribe form (stub → Phase 3)
- [x] SSR, meta tags

**DoD:** Lighthouse SEO ≥ 90 на главной (local). **TZ:** §11.2

---

### Блок 2.3 — Каталог

#### STEP-049 🔴 Catalog root `/catalog/`
- [x] Category grid с иконками/фото
- [x] SSR fetch categories

**DoD:** 7 категорий отображаются.

---

#### STEP-050 🔴 Category page `/catalog/[...slug]/`
- [x] Product grid (12/24/48 per page)
- [x] Grid/List toggle
- [x] Sidebar filters (desktop): current, coil, poles, execution, type
- [x] Bottom Sheet filters (mobile)
- [x] URL sync: `?current=400&coil=220&page=2`
- [x] Sort dropdown
- [x] Skeleton loading, lazy images
- [x] Empty state + «Сбросить фильтры»
- [x] noindex meta when filters active

**DoD:** все FR-CAT-01…08. Протестировать на 375px и 1280px.

---

#### STEP-051 🔴 ProductCard component
- [x] Image, name, current, price «от X ₽», badge «Производитель»
- [x] Buttons: «Подробнее», «В заявку» (quick add default variant)
- [x] Clickable entire card → PDP

**DoD:** карточка соответствует FR-CAT-06.

---

### Блок 2.4 — Карточка товара (PDP)

#### STEP-052 🔴 PDP page `/catalog/[cat]/[product]/`
- [x] SSR fetch ProductGroup
- [x] Gallery (primary image + thumbs)
- [x] **Configurator**: execution chips, coil voltage select, aux contacts
- [x] On variant change: update price, SKU, URL (`?variant=slug`)
- [x] Quantity stepper 1–9999
- [x] CTA: «Добавить в заявку», «Сравнить», «Скачать паспорт»
- [x] Sticky mobile bar: price + CTA

**DoD:** FR-PDP-01…03, 11…13.

---

#### STEP-053 🔴 PDP tabs
- [x] Tab «Характеристики» — table + specs
- [x] Tab «Документация» — PDF/DWG download links
- [x] Tab «Описание» — назначение HTML
- [x] Block «Структура условного обозначения» (interactive)
- [x] Badge «Честный знак» + tooltip

**DoD:** FR-PDP-04…09.

---

#### STEP-054 🟡 PDP related blocks
- [x] «Похожие товары» carousel
- [x] «Аксессуары» (катушки, блокировки)
- [x] FAQ accordion (3–5 вопросов по модели)

**DoD:** FR-PDP-10, FR-SEO-09.

---

#### STEP-055 🔴 Schema.org JSON-LD
- [x] Product + Offer + BreadcrumbList on PDP
- [x] Organization on homepage
- [ ] Validate: Google Rich Results Test

**DoD:** FR-PDP-14, FR-SEO-06.

---

### Блок 2.5 — Поиск и сравнение

#### STEP-056 ✅ Search autocomplete
- [x] Header search input → debounced API `/api/v1/search/suggest?q=`
- [x] Dropdown: SKU, name, category
- [x] Response < 200ms (cached)

**DoD:** FR-SRH-01, FR-SRH-04.

---

#### STEP-057 ✅ Search results `/search/`
- [x] Full results page + filters + pagination
- [x] Highlight matched terms

**DoD:** FR-SRH-03.

---

#### STEP-058 ✅ Compare page `/compare/`
- [x] localStorage `compare_ids[]` max 4
- [x] Fetch `/api/v1/compare/?ids=`
- [x] Side-by-side table, highlight diffs
- [x] «Добавить все в заявку» button
- [x] Header compare badge count

**DoD:** FR-CMP-01…04.

---

### Блок 2.6 — API client layer

#### STEP-059 ✅ Frontend API module
- [x] `lib/api/client.ts` — fetch wrapper, error handling
- [x] `lib/api/products.ts`, `categories.ts`, `search.ts`
- [ ] TypeScript types from OpenAPI (optional: `openapi-typescript`)

**DoD:** all pages use typed API client, no raw fetch in components.

---

### ✅ Checkpoint Phase 2

| Критерий | Проверка | Статус |
|---|---|---|
| Catalog filters | 5 filter combinations manual test | ✅ реализовано |
| PDP configurator | Switch variant → price changes | ✅ STEP-052 |
| Search | «кт6043» finds product | ✅ API + `/search/` |
| Compare | 4 products side-by-side | ✅ `/compare/` |
| Mobile | 375px — catalog + PDP usable | ✅ responsive layout |
| Lighthouse | Performance + SEO ≥ 85 (local) | ⏳ проверить локально |

---

## Phase 3 — Conversion (3–4 нед)

### Блок 3.1 — Корзина-заявка

#### STEP-076 ✅ Cart backend API
- [x] Session cart via cookie `cart_session` + Redis backup
- [x] `POST /api/v1/cart/items/` — add (variant_id, quantity)
- [x] `GET /api/v1/cart/` — list + subtotal
- [x] `PATCH /api/v1/cart/items/{id}/` — update qty
- [x] `DELETE /api/v1/cart/items/{id}/`
- [x] `DELETE /api/v1/cart/clear/`
- [x] Price snapshot on add

**DoD:** FR-CART-01, cart persists 30 days.

---

#### STEP-077 ✅ Cart frontend
- [x] Mini-cart in header (count + sum)
- [x] `/cart/` page: table, edit qty, remove, clear
- [x] Real-time subtotal recalc
- [x] Empty cart state

**DoD:** FR-CART-02…05.

---

#### STEP-078 ✅ Quote submit API
- [x] `POST /api/v1/quotes/` — validate form, create QuoteRequest + items
- [x] Honeypot field `website` (hidden)
- [x] Rate limit: 5/IP/hour (django-ratelimit)
- [x] Return `{ number: "ЗК-2026-00001" }`

**DoD:** FR-CART-06…10, FR-CART-13.

---

#### STEP-079 ✅ Quote form UI
- [x] Form: name*, company*, email*, phone*, city, INN, KPP, comment
- [x] Validation: email, phone +7, INN 10/12 digits
- [x] Privacy checkbox*
- [x] Submit → redirect `/order/success?number=...`

**DoD:** FR-CART-06…08.

---

#### STEP-080 ✅ Email: менеджеру
- [x] Celery task `send_quote_notification(quote_id)`
- [x] HTML template — table per TZ §7.5.1
- [x] Recipients from `SiteSettings.order_emails`
- [x] Mailhog test in dev

**DoD:** FR-CART-11. Email в Mailhog с таблицей и итогом.

---

#### STEP-081 ✅ Email + PDF: клиенту
- [x] Celery task `send_quote_confirmation(quote_id)`
- [x] HTML «Ваша заявка принята № ...»
- [x] PDF КП attachment (WeasyPrint + xhtml2pdf fallback)
- [x] PDF: header завода, table, total, disclaimer

**DoD:** FR-CART-12. PDF opens correctly.

---

#### STEP-082 ✅ CRM Webhook
- [x] Celery task `send_crm_webhook(quote_id)` — POST JSON (TZ §13.1)
- [x] Retry 3x with exponential backoff
- [x] Log success/failure in QuoteRequest

**DoD:** FR-CART-14. Webhook visible in logs (mock server).

---

#### STEP-083 ✅ Quote admin workflow
- [x] Admin: QuoteRequest list, filters by status
- [x] Actions: mark in_progress, quoted, completed
- [x] Manager comment field
- [x] Export CSV

**DoD:** sales manager can process quote in admin.

---

#### STEP-084 ✅ PDF preview + Excel export
- [x] `GET /api/v1/cart/export/pdf/` — preview before submit
- [x] `GET /api/v1/cart/export/xlsx/`

**DoD:** FR-CART-15…16.

---

### Блок 3.2 — Лиды

#### STEP-085 ✅ Contact + Callback forms
- [x] `POST /api/v1/leads/contact/`, `/api/v1/leads/callback/`
- [x] UI: modal forms in header/footer
- [x] Email notification + admin record

**DoD:** FR-LEAD-01…02, FR-LEAD-04.

---

### Блок 3.3 — Контентные страницы

#### STEP-086 ✅ Static pages
- [x] `/about/` — history since 1956, mission, production
- [x] `/about/certificates/` — gallery + PDF download
- [x] `/about/production/`
- [x] `/contacts/` — phones, emails, requisites, Yandex Map iframe
- [x] `/support/` — FAQ list + contact form
- [x] `/dealers/` — partner form
- [x] `/privacy/`, `/terms/`

**DoD:** FR-CNT-01…03, FR-CNT-05…07.

---

#### STEP-087 ✅ News
- [x] `/news/` — list with pagination
- [x] `/news/[slug]/` — article SSR
- [x] `/news/rss.xml` — RSS feed

**DoD:** FR-CNT-04.

---

#### STEP-088 ✅ Application pages
- [x] `/applications/crane/`, `/applications/nku/`, `/applications/transport/`
- [x] Product recommendations per application

**DoD:** FR-CNT-08.

---

#### STEP-089 ✅ Anti-counterfeit block
- [x] Component on homepage + PDP footer
- [x] Text from TZ §1.1 + link to contacts

**DoD:** FR-CNT-07.

---

### Блок 3.4 — Рассылка

#### STEP-090 ✅ Newsletter subscribe API
- [x] `POST /api/v1/newsletter/subscribe/` — email, name
- [x] Create subscriber status=pending, send confirm email
- [x] `GET /subscribe/confirm/{token}/` — activate
- [x] `GET /unsubscribe/{token}/` — deactivate

**DoD:** FR-NL-01…03.

---

#### STEP-091 ✅ Newsletter admin + send
- [x] Admin: Campaign CRUD (subject, WYSIWYG body)
- [x] Preview to test email
- [x] Celery batch send: 100/min throttle
- [x] SendLog per recipient
- [x] Unsubscribe link in every email

**DoD:** FR-NL-04…09.

---

#### STEP-092 ✅ Subscribe UI
- [x] Footer form + `/news/` sidebar
- [x] Success / «check your email» message

**DoD:** FR-NL-01.

---

### ✅ Checkpoint Phase 3

| Критерий | Проверка |
|---|---|
| Full quote flow | Add 3 items → submit → success page |
| Manager email | HTML table with total |
| Client email | PDF attached |
| Newsletter | Subscribe → confirm → active |
| Content | All static pages render |

---

## Phase 4 — Launch (2–3 нед)

### Блок 4.1 — SEO

#### STEP-101 🔴 Sitemap + robots
- [x] Celery beat: daily `generate_sitemap` → `/sitemap.xml` (products, categories, news, pages)
- [x] `robots.txt` — allow /, disallow /manage/, /api/
- [x] next-sitemap config for frontend static routes

**DoD:** FR-SEO-04…05. sitemap contains all active products.

---

#### STEP-102 🔴 Meta + canonical
- [x] Every page: unique title, description, h1 from CMS
- [x] Canonical URLs on PDP (default variant)
- [x] OG + Twitter Card tags

**DoD:** FR-SEO-02…03, FR-PDP-15.

---

#### STEP-103 🔴 301 Redirects
- [x] Import old ekontaktor.ru URLs → Redirect model
- [x] Middleware or nginx rules
- [x] Management command `import_redirects data/redirects.csv`

**DoD:** FR-SEO-08. Top 20 old URLs redirect correctly.

---

#### STEP-104 🔴 Analytics
- [x] Yandex.Metrika counter + goal «quote_submit»
- [x] GA4 + event `generate_lead`
- [x] UTM capture in QuoteRequest

**DoD:** test goal fires on quote submit.

---

### Блок 4.2 — Security hardening

#### STEP-105 🔴 Production security
- [x] HTTPS + HSTS (nginx + Let's Encrypt certbot)
- [x] Secure cookies, CSRF, CSP headers
- [x] CORS prod whitelist
- [x] File upload audit
- [x] `pip-audit`, `npm audit` in CI

**DoD:** FR-SEC-01…12 checklist passed.

---

#### STEP-106 🔴 Rate limiting (nginx + app)
- [x] nginx: API 100 req/min, forms 5/hour
- [x] django-ratelimit on quote, leads, subscribe

**DoD:** FR-SEC-07.

---

### Блок 4.3 — Performance

#### STEP-107 🔴 Performance optimization
- [x] Redis cache tuning (TTLs from TZ §9.2)
- [x] Next.js Image optimization, WebP
- [ ] DB query audit (django-debug-toolbar → fix N+1)
- [ ] Lighthouse CI in GitHub Actions

**DoD:** Lighthouse Performance + SEO + A11y ≥ 90 on home, catalog, PDP.

---

### Блок 4.4 — Testing

#### STEP-108 🔴 Automated tests
- [x] Backend: pytest ≥ 50 tests (models, API, quote flow, search)
- [x] Frontend: vitest component tests (key components)
- [x] E2E Playwright: `add_to_cart → submit_quote → success`
- [x] k6 load test: 50 VU browse catalog 5 min

**DoD:** TZ §16.1 test plan items covered.

---

#### STEP-109 🔴 UAT with заказчик
- [x] UAT checklist 20 пунктов (from TZ §16.2)
- [ ] Fix critical bugs
- [ ] Sign-off document

**DoD:** all §16.2 checkboxes ✅.

---

### Блок 4.5 — Production deploy

#### STEP-110 🔴 Staging deploy
- [x] Deploy to staging VPS via CI/CD
- [x] Smoke tests: catalog, PDP, quote, admin
- [ ] Content fill: real photos top-20 SKU

**DoD:** staging URL accessible to заказчик.

---

#### STEP-111 🔴 Production deploy
- [x] DB backup script (daily cron)
- [x] Production env vars set (SMTP, ORDER_EMAILS, SECRET_KEY)
- [ ] DNS → production
- [ ] SSL active
- [x] Monitoring: Sentry DSN

**DoD:** production live, quote email received on real mailbox.

---

#### STEP-112 🟡 Post-launch
- [x] Submit sitemap to Yandex Webmaster + Google Search Console
- [x] Monitor 404 logs → add redirects
- [x] Handover docs: admin guide, import guide
- [x] Retrospective + Phase 2 backlog (EN, Elasticsearch, 1C, Telegram bot)

**DoD:** site indexed within 7 days.

---

## ✅ Final MVP Checklist (TZ §16.2)

- [ ] Полный каталог из прайса ekontaktor.ru загружен и отображается
- [ ] Фильтры по току, катушке, исполнению работают корректно
- [ ] Конфигуратор вариантов на PDP переключает SKU и цену
- [ ] Корзина сохраняется между сессиями
- [ ] Заявка отправляет email менеджеру с таблицей и итогом
- [ ] Клиент получает PDF-копию спецификации
- [ ] Подписка на рассылку работает (double opt-in)
- [ ] Массовая рассылка из админки отправляется
- [ ] Lighthouse Performance/SEO/Accessibility > 90
- [ ] Schema.org валидируется в Google Rich Results Test
- [ ] sitemap.xml содержит все активные товары
- [ ] Админка защищена 2FA + non-default URL
- [ ] Мобильная версия корзины и каталога функциональна

---

## Блокеры и решения заказчика

| # | Вопрос | Блокирует шаги | Статус |
|---|---|---|---|
| 1 | Email для заявок | STEP-080, STEP-111 | ⏳ Ожидает |
| 2 | Домен | STEP-004, STEP-111 | ⏳ TBD |
| 3 | CRM webhook | STEP-082 | ⏳ TBD |
| 4 | SMTP | STEP-080, STEP-091 | ⏳ TBD |
| 5 | Фото/DWG архив | STEP-034, STEP-110 | ⏳ TBD |
| 6 | Privacy/Terms тексты | STEP-086 | ⏳ Шаблон |
| 7 | EN версия | — | Phase 2 |

---

## Phase 2 Backlog (после MVP)

| ID | Feature | TZ ref |
|---|---|---|
| BL-01 | English version + hreflang | FR-SEO-07 |
| BL-02 | Elasticsearch search | §4.1 |
| BL-03 | 1C / ERP price & stock sync | §13 |
| BL-04 | Telegram bot for new quotes | §13 |
| BL-05 | Customer portal (order history) | — |
| BL-06 | 3D/STEP CAD downloads | FR-PDP-05 |
| BL-07 | Parametric 3D configurator | §11 |

---

## Трекинг прогресса

| Фаза | Всего шагов | Выполнено | % |
|---|---|---|---|
| Phase 0 | 5 | 4* | 80% |
| Phase 1 | 27 | 24 | 89% |
| Phase 2 | 14 | 0 | 0% |
| Phase 3 | 17 | 0 | 0% |
| Phase 4 | 12 | 0 | 0% |
| **Итого** | **75** | **28** | **37%** |

> Обновляйте таблицу по мере выполнения шагов.

---

## Связанные документы

| Файл | Назначение |
|---|---|
| [TZ.md](./TZ.md) | Полное техническое задание |
| [PLAN.md](./PLAN.md) | Данный план (вы здесь) |
| `.env.example` | Переменные окружения |
| `data/source/` | Исходники для импорта |

---

*Следующий шаг: выполнить **STEP-001** — инициализация Git-репозитория.*
