# URL и внутренние ссылки — техническое задание

Документ фиксирует канонический формат URL на сайте [ekontaktor.ru](https://www.ekontaktor.ru) и критерии приёмки для редиректов и внутренних ссылок.

---

## 1. Канонический формат URL

| Тип | Правило | Пример |
|-----|---------|--------|
| Статические страницы | trailing slash | `/news/`, `/partners/`, `/about/` |
| Каталог (категория) | полный MPTT-путь | `/catalog/kontaktory-kt/kt-6000b/` |
| Карточка товара | MPTT + slug группы | `/catalog/kontaktory-kt/kt-6000b/kontaktor-kt-6043/` |
| Legacy CMS | только 301 на канон | `/company/news/?id=98` → `/news/` |
| Файлы старого сайта | 301 на раздел | `/files/cat/*.doc` → `/catalog/` |

**Запрещено:** редирект, если `normalize(old) == normalize(new)` — это вызывает `ERR_TOO_MANY_REDIRECTS`.

---

## 2. Слои редиректов (приоритет)

1. **Next.js middleware** — только для legacy-путей (`/company/*`, `/files/*`, старый `/catalog/{section}/` с `?id=`).
2. **Legacy resolver** (`data/legacy_site.yaml` + `resolve_legacy_path`) — старые URL CMS.
3. **Redirect model** — CSV (`data/redirects.csv`), `sync_product_catalog_redirects`, `sync_legacy_site_redirects`.
4. **In-page 301** — канонизация пути товара в `catalog/[...slug]/page.tsx`.

Единая точка резолва API: `GET /api/v1/redirects/resolve/?path=...&query=...` → `apps.seo.services.redirect_resolve.resolve_redirect()`.

---

## 3. Область покрытия «все ссылки»

| Источник | Файлы / механизм |
|----------|------------------|
| Навигация | `catalog-meta.ts`, `Header`, `Footer` |
| Каталог | `catalog-url.ts`, `ProductCard`, `CategoryCard` |
| SEO | `sitemap.py`, schema, metadata |
| Legacy | `legacy_site.yaml`, `redirects.csv` |
| API paths | `product_catalog_path()`, serializers `category_path` |

---

## 4. Критерии приёмки

- [ ] Главная и все маршруты из `frontend/src/app/**/page.tsx` открываются без redirect loop.
- [ ] `python manage.py audit_site_urls --fail-on-error` — 0 ошибок.
- [ ] `python manage.py audit_redirect_loops --fail-on-error` — 0 петель.
- [ ] `python manage.py audit_internal_links --fail-on-error` — 0 ошибок.
- [ ] curl top legacy URL → 301 на валидную страницу (200).
- [ ] Внутренние ссылки в sitemap = href в UI = `product_catalog_path()` в API.

---

## 5. Команды обслуживания

```bash
python manage.py purge_redirect_loops
python manage.py sync_legacy_site_redirects
python manage.py sync_product_catalog_redirects
python manage.py audit_redirect_loops --fail-on-error
python manage.py audit_internal_links --fail-on-error
python manage.py audit_site_urls --fail-on-error
```

---

## 6. curl-чеклист (prod)

| URL | Ожидание |
|-----|----------|
| `https://www.ekontaktor.ru/` | 200 |
| `https://www.ekontaktor.ru/news/` | 200 |
| `https://www.ekontaktor.ru/partners/` | 200 |
| `https://www.ekontaktor.ru/company/news/?id=98` | 301 → `/news/` |
| `https://www.ekontaktor.ru/company/dilers/` | 301 → `/partners/` |
| `https://www.ekontaktor.ru/files/cat/test.doc` | 301 → `/catalog/` |
| `https://www.ekontaktor.ru/catalog/contactor/?id=19` | 301 → категория КТ 6000 |

---

## 7. Что не входит в legacy-маппинг

Не добавлять в `legacy_site.yaml` канонические URL нового сайта:

- `/news`, `/news/` → `/news/`
- `/catalog`, `/catalog/` → `/catalog/`
- `/partners`, `/about`, `/contacts` и т.д.

Эти пути — целевые страницы, не источники редиректа.

---

*См. также: `docs/DEPLOY-BEGET.md` §8–9, `AGENTS.md` §1.*
