# Design System — АО «Электроконтактор»

> **STEP-005** · Phase 0  
> Краткая выжимка токенов. **Полная спецификация:** [DESIGN_TZ.md](./DESIGN_TZ.md)  
> Функциональное ТЗ: [TZ.md §11](../../TZ.md)

## Палитра (Variant B — Синий + Терракотовый)

| Token | HEX | Использование |
|---|---|---|
| `--color-brand-blue` | `#0077AF` | Header links, H1–H3, навигация, primary buttons |
| `--color-brand-blue-light` | `#E5F1F8` | Фон артикула, плашки «Производитель» |
| `--color-brand-blue-dark` | `#005684` | Header, footer, hero gradient start |
| `--color-brand-blue-darker` | `#003456` | Hero gradient end |
| `--color-cta` | `#E87A20` | CTA «В заявку», «Отправить заявку», бейдж «Хит» |
| `--color-cta-hover` | `#C96815` | Hover CTA |
| `--color-text-primary` | `#1A2530` | Основной текст, цены |
| `--color-text-secondary` | `#5A6B7C` | Подписи, артикулы, labels |
| `--color-bg-light` | `#F6F9FC` | Фон секций |
| `--color-border-light` | `#DCE4EC` | Рамки карточек, таблицы |
| `--color-success` | `#2E9B5C` | «В наличии» |
| `--color-error` | `#DC2626` | Ошибки валидации |

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
| Button | `default` (brand blue) | «Подробнее», «Применить фильтр», «Скачать чертёж» |
| Button | `accent` (terracotta) | «В заявку», «Отправить заявку» |
| Button | `outline` | Синяя обводка, вторичные действия |
| Badge | `brand` | «Производитель» |
| Badge | `accent` / `hit` | «Хит продаж», акции |
| Badge | `neutral` | «Честный знак» |
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
