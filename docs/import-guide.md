# Импорт каталога (XLSX)

## Формат файла

Колонки (лист «products»):

| Колонка | Описание |
|---------|----------|
| category_path | Путь категорий через `/`, напр. `Контакторы КТ/Серия 6000` |
| group_name | Название группы |
| group_slug | URL slug группы |
| sku_code | Артикул SKU |
| execution | B / C |
| coil_voltage_v | Напряжение катушки |
| price | Цена |
| is_default | 1 / 0 |

## Команда

```bash
python manage.py import_catalog path/to/catalog.xlsx
```

## Редиректы (legacy URL)

```bash
python manage.py import_redirects data/redirects.csv
```

CSV: `old_path,new_path` — пути с ведущим `/`.

## После импорта

1. Пересборка поискового индекса: `python manage.py rebuild_search_index`
2. Регенерация sitemap: `python manage.py generate_sitemap`
