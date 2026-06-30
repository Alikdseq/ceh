# Design System — АО «Электроконтактор»

> **STEP-005** · Phase 0  
> Основа для Next.js + Tailwind. См. [TZ.md §11](../../TZ.md).

## Палитра

| Token | HEX | Использование |
|---|---|---|
| `--color-navy` | `#0A1628` | Header, footer, hero background |
| `--color-navy-light` | `#1A2744` | Cards on dark, hover states |
| `--color-primary` | `#0066CC` | Links, active filters, secondary CTA |
| `--color-primary-hover` | `#0052A3` | Hover links |
| `--color-accent` | `#F59E0B` | **Только** CTA «В заявку», cart badge |
| `--color-accent-hover` | `#D97706` | Hover CTA |
| `--color-surface` | `#FFFFFF` | Page background |
| `--color-muted` | `#F4F6F8` | Section backgrounds, table stripes |
| `--color-border` | `#E2E8F0` | Borders, dividers |
| `--color-text` | `#1E293B` | Body text |
| `--color-text-muted` | `#64748B` | Secondary text, labels |
| `--color-success` | `#059669` | In stock badge |
| `--color-error` | `#DC2626` | Validation errors |

## Типографика

| Роль | Шрифт | Размер (desktop) | Weight |
|---|---|---|---|
| H1 | Manrope | 40px / 2.5rem | 700 |
| H2 | Manrope | 32px / 2rem | 600 |
| H3 | Manrope | 24px / 1.5rem | 600 |
| Body | Inter | 16px / 1rem | 400 |
| Small | Inter | 14px / 0.875rem | 400 |
| SKU / артикул | JetBrains Mono | 14px | 500 |
| Price | Manrope | 28px | 700 |

```css
/* design/tokens.css — подключить в frontend */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Manrope:wght@600;700&family=JetBrains+Mono:wght@500&display=swap');
```

## Spacing & Layout

| Token | Value |
|---|---|
| Container max-width | `1280px` |
| Grid gap (catalog) | `24px` |
| Section padding Y | `64px` desktop / `40px` mobile |
| Border radius card | `8px` |
| Border radius button | `6px` |
| Shadow card | `0 1px 3px rgba(10,22,40,0.08)` |

## Компоненты (shadcn/ui mapping)

| Компонент | Вариант | Применение |
|---|---|---|
| Button | `default` (primary blue) | «Подробнее», «Сравнить» |
| Button | `accent` (orange) | «В заявку», «Отправить заявку» |
| Button | `outline` | «Скачать паспорт» |
| Badge | `manufacturer` | «Производитель» |
| Badge | `honest-sign` | «Честный знак» |
| Card | product | Каталог grid |
| Sheet | — | Mobile filters, mobile nav |
| Tabs | — | PDP: характеристики / документация |
| Table | — | Specs, cart, compare |

## Иконки

- **Lucide React** — единый набор
- Размер: 20px inline, 24px navigation

## Breakpoints

| Name | Min width |
|---|---|
| `sm` | 640px |
| `md` | 768px |
| `lg` | 1024px |
| `xl` | 1280px |

## Accessibility

- Конtrast ratio ≥ 4.5:1 для текста
- Focus ring: `2px solid #0066CC`, offset 2px
- Touch targets ≥ 44×44px на mobile

## Файлы

| Файл | Назначение |
|---|---|
| [design/tokens.css](../../design/tokens.css) | CSS-переменные |
| [wireframes/README.md](./wireframes/README.md) | Wireframes 5 экранов |

## Figma

> Figma-макет создаётся заказчиком/дизайнером на основе wireframes.  
> До появления Figma — разработка ведётся по tokens + wireframes.
