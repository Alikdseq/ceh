# Core Web Vitals — ekontaktor.ru

Рекомендации по шаблонам страниц (проверка через [PageSpeed Insights](https://pagespeed.web.dev/) после деплоя).

## Целевые метрики (TZ FR-SEO-11)

| Метрика | Цель |
|--------|------|
| LCP | &lt; 2.5 s |
| CLS | &lt; 0.1 |
| INP | &lt; 200 ms |

## URL для замера

1. `/` — главная (hero, featured, шрифты)
2. `/catalog/kontaktory-kt/` — листинг категории
3. Карточка P0-товара (например КТ6023)
4. `/pricelist/`
5. `/dealers/`

## Уже реализовано в коде

- LCP-изображение на PDP: `priority` + `sizes` в [`ProductGallery.tsx`](../../frontend/src/components/product/ProductGallery.tsx)
- SSR каталога и карточек — быстрый первый HTML
- `noindex` для фасетных URL — меньше краул-бюджета на дубли

## Рекомендации (очередь оптимизации)

1. **Изображения:** WebP в `/tovar/`, не грузить оригиналы &gt; 200 KB без необходимости; для hero на главной — явные `width`/`height` или aspect-ratio.
2. **Шрифты:** `next/font` уже используется; держать только latin+cyrillic subsets.
3. **Третьи стороны:** Metrika/GA4 — отложенная загрузка через `AnalyticsProvider`; не блокировать main thread.
4. **PDF:** не встраивать тяжёлые PDF в iframe на landing — только ссылки.
5. **CDN/nginx:** gzip/brotli для HTML/JS/CSS; cache static `/tovar/`, `/_next/static/`.

## Prod checklist

- [ ] PSI mobile + desktop для 5 URL выше
- [ ] Яндекс.Вебмастер → «Скорость загрузки» без критичных ошибок
- [ ] Исправить URL с LCP &gt; 4 s (обычно крупное фото или медленный TTFB)
