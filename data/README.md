# Исходные данные для импорта каталога

| Файл | Описание |
|---|---|
| `source/КАТАЛОГ КОНТАКТОРОВ 2026.pdf` | Официальный PDF-каталог (48 стр., 81 модель) |
| `source/catalog_extract.txt` | Текст, извлечённый из PDF (reference для парсера) |
| `categories.yaml` | Дерево категорий MPTT (7 корневых разделов) |
| `pricelist.csv` | Прайс ekontaktor.ru — 89 позиций с ценами |
| `CLIENT_INPUT.md` | Входные данные и чеклист от заказчика |

## Импорт (Phase 1)

```bash
python manage.py import_categories data/categories.yaml
python manage.py import_pricelist data/pricelist.csv
python manage.py import_catalog_pdf data/source/КАТАЛОГ\ КОНТАКТОРОВ\ 2026.pdf
```

## Статистика pricelist.csv

- Контакторы КТ/КТП/КТЭ: 72 позиции
- Аксессуары: 6 позиций
- Выключатели: 3 позиции
- Кулачковые элементы: 7 позиций
- Пакетные переключатели: 6 позиций

**Источник цен:** https://www.ekontaktor.ru/pricelist/ (на дату 30.06.2026)
