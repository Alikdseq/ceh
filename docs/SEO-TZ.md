# SEO-ТЗ — ekontaktor.ru

Операционное техническое задание на поисковую оптимизацию B2B-сайта АО «Владикавказский завод «Электроконтактор». Дополняет [TZ.md](../TZ.md) §9 (FR-SEO-01…11).

**Домен канонический:** `https://www.ekontaktor.ru`  
**Семантическое ядро (данные):** [data/seo/semantic-core.yaml](../data/seo/semantic-core.yaml)

---

## 1. Цели и KPI

| KPI | Инструмент | Целевой ориентир (12 мес.) |
|-----|------------|----------------------------|
| Органические сессии | Яндекс.Метрика / GA4 | +50% к baseline после миграции |
| Клики из поиска | GSC + Яндекс.Вебмастер | рост MoM |
| Позиции P0-запросов | Topvisor / Serpstat | ТОП-3 по бренду и топ-20 моделям |
| Заявки organic | CRM / QuoteRequest + UTM | отслеживание `utm_source=organic` |
| Индексируемые URL | GSC «Страницы» | 100% активных ProductGroup без ошибок |
| Core Web Vitals | PSI / Вебмастер | LCP &lt; 2.5s, CLS &lt; 0.1 на home, category, PDP |

**Не является KPI контракта:** гарантия «1-е место по всем запросам» — зависит от конкурентов и ссылочного профиля.

---

## 2. Семантическое ядро

Кластеры (см. YAML):

- **Коммерческий** — модель + «купить / цена / опт / прайс» → карточка товара или `/pricelist/`.
- **Технический** — габариты, характеристики, обозначение → PDP + документы.
- **Брендовый** — «электроконтактор», «честный знак» → главная, about.
- **Партнёрский** — дилеры → `/dealers/`, `/partners/`.
- **Информационный** — выбор, сравнения → `/news/`.
- **Применения** — отрасли → `/applications/{slug}/`.
- **Региональный** — «доставка в {город}» → `/delivery/{city-slug}/` (только при уникальном intro и `is_indexable`).

Команда отчёта: `python manage.py map_semantic_to_pages`.

---

## 3. Технические требования

| ID | Требование | Реализация |
|----|------------|------------|
| FR-SEO-01 | SSR карточек и каталога | Next.js App Router |
| FR-SEO-02 | Уникальные title/description/h1 | CMS + `lib/seo.ts` |
| FR-SEO-03 | ЧПУ каталога | `product_catalog_path` |
| FR-SEO-04 | sitemap auto | Celery `generate_sitemap` daily |
| FR-SEO-05 | robots + canonical | `robots.ts`, `buildPageMetadata` |
| FR-SEO-06 | JSON-LD | `lib/schema.ts` |
| FR-SEO-08 | 301 legacy | `Redirect` + middleware |
| FR-SEO-09 | FAQ на PDP / support | ProductFAQ, FAQPage |
| FR-SEO-10 | noindex фасетов | `shouldNoindexCatalogParams` |
| FR-SEO-11 | CWV | см. [docs/seo/CWV-AUDIT.md](./seo/CWV-AUDIT.md) |

### Post-migration checklist

1. `NEXT_PUBLIC_SITE_URL` и `FRONTEND_URL` = `https://www.ekontaktor.ru`.
2. Добавить сайт в [Яндекс.Вебмастер](https://webmaster.yandex.ru) и [Google Search Console](https://search.google.com/search-console).
3. Отправить `https://www.ekontaktor.ru/sitemap.xml`.
4. Проверить 301 из [data/redirects.csv](../data/redirects.csv).
5. Включить IndexNow: `INDEXNOW_ENABLED=true`, ключ в `.env`, файл `frontend/public/{KEY}.txt`.
6. `python manage.py rebuild_search_index` после массового контента.
7. Запросить переобход топ-100 URL (PDP P0, категории, главная).

### Robots и поиск на сайте

- `/search` с параметром `q` — **noindex** (robots disallow + meta).
- **SearchAction** в JSON-LD указывает на `/search?q=` для sitelinks search box; индексируется только поведение redirect resolve на PDP для модельных запросов через внутренний поиск (не как отдельная landing).

---

## 4. Контент-стандарты

### Карточка товара (PDP)

- Минимум **800 символов** уникального текста в `full_description` (не считая таблицу характеристик).
- Обязательные блоки (H2): **Назначение**, **Преимущества**, **Область применения**; при наличии — **Условное обозначение**, ссылка на документы.
- `meta_title` ≤ 60 символов, `meta_description` 140–160 символов.
- 3–5 FAQ на карточку (поле ProductFAQ или генерация).

### Новости

- 2–4 материала в месяц; перелинковка на 1–3 товара/категории.

### Кейсы

- 1 кейс в месяц; `/cases/{slug}/`; отрасль + продукты.

### Региональные страницы

- Индексируются только при `is_indexable=true` и **≥ 400 символов** уникального `intro_html`.
- Комбинации city×category — только с уникальным текстом в `CityCategoryLanding`.

---

## 5. Link building

См. [docs/seo/LINK-BUILDING.md](./seo/LINK-BUILDING.md). Запрещены биржи и массовые автоматические ссылки.

---

## 6. Региональная политика

- Базовый URL: `/delivery/{city-slug}/`.
- Опционально: `/delivery/{city-slug}/{category-slug}/` — noindex без уникального intro.
- Импорт городов: `data/seo/cities.yaml`, команда `import_delivery_cities`.

---

## 7. UAT SEO

См. расширенный блок в [docs/UAT-CHECKLIST.md](./UAT-CHECKLIST.md).

---

## 8. Ответственность и этапы

| Этап | Содержание |
|------|------------|
| 1 | Техника: sitemap, schema, IndexNow, CWV |
| 2 | Семантика, applications, перелинковка |
| 3 | Контент PDP, новости, кейсы |
| 4 | Регионы |
| 5 | Внешние ссылки, NAP, PR |

Деплой: [docs/seo/DEPLOY-RUNBOOK.md](./seo/DEPLOY-RUNBOOK.md).
