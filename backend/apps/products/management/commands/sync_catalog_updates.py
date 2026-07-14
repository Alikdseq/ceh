"""
Синхронизация каталога: габариты, цены (+22% НДС), фото, хиты продаж.
Запуск на сервере после деплоя:
  python manage.py sync_catalog_updates
"""
from __future__ import annotations

import csv
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.core.paths import resolve_data_file
from apps.products.contactor_dimensions import dimensions_for
from apps.products.models import ProductGroup, ProductSpec
from apps.products.utils import invalidate_catalog_cache

VAT_MULTIPLIER = Decimal("1.22")

PVP_PRICES_WITH_VAT = {
    "ПВП 17-29 (63А) 2-пакетный": 3240,
    "ПВП 17-29 (63А) 3-пакетный": 3950,
    "ПВП 17-29 (63А) 5-пакетный": 6400,
    "ПВП 17-31 (100А) 2-пакетный": 3660,
    "ПВП 17-31 (100А) 3-пакетный": 4370,
    "ПВП 17-31 (100А) 5-пакетный": 8650,
}

KT6032BS_ROW = {
    "category": "Контакторы",
    "sku_name": "КТ 6032БС (250А)",
    "price_rub": "21425",
    "nominal_current_a": "250",
    "product_type": "KT",
    "notes": "исполнение БС",
}

FEATURED_SERIES = ("6023", "6033", "6043", "6053")

ROTATE_IMAGES = (
    "КТ6053.JPG",
    "КТП6014.JPG",
)

SPEC_KEY = "overall_dimensions"


class Command(BaseCommand):
    help = "Apply dimensions, VAT prices, featured products, rotate selected photos"

    def add_arguments(self, parser):
        parser.add_argument("--skip-prices", action="store_true")
        parser.add_argument("--skip-dimensions", action="store_true")
        parser.add_argument("--skip-featured", action="store_true")
        parser.add_argument("--skip-images", action="store_true")

    @transaction.atomic
    def handle(self, *args, **options):
        if not options["skip_dimensions"]:
            self._apply_dimensions()
        if not options["skip_prices"]:
            self._update_pricelist_csv()
            call_command("import_pricelist", "/data/pricelist.csv")
        if not options["skip_featured"]:
            self._set_featured()
        if not options["skip_images"]:
            self._rotate_images()
        invalidate_catalog_cache()
        self.stdout.write(self.style.SUCCESS("Catalog sync complete"))

    def _apply_dimensions(self) -> None:
        updated = 0
        groups = ProductGroup.objects.filter(
            is_active=True,
            product_type__in=("KT", "KTP"),
        ).exclude(series_code="")
        for group in groups:
            dims = dimensions_for(group.product_type, group.series_code)
            if not dims:
                continue
            _, created = ProductSpec.objects.update_or_create(
                group=group,
                spec_key=SPEC_KEY,
                defaults={
                    "spec_value": dims.as_spec_value(),
                    "spec_unit": "",
                    "filterable": False,
                    "sort_order": 900,
                },
            )
            if created:
                updated += 1
            else:
                updated += 1
        self.stdout.write(f"  Dimensions: {updated} product cards")

    def _update_pricelist_csv(self) -> None:
        path = resolve_data_file("data/pricelist.csv")
        rows = list(csv.DictReader(path.open(encoding="utf-8")))
        fieldnames = rows[0].keys() if rows else [
            "category", "sku_name", "price_rub", "nominal_current_a", "product_type", "notes",
        ]
        new_rows: list[dict] = []
        inserted_6032bs = False

        for row in rows:
            name = row["sku_name"]
            if name in PVP_PRICES_WITH_VAT:
                row["price_rub"] = str(PVP_PRICES_WITH_VAT[name])
            else:
                net = Decimal(str(row["price_rub"]).replace(" ", "").replace(",", "."))
                gross = (net * VAT_MULTIPLIER).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
                row["price_rub"] = str(int(gross))
            new_rows.append(row)
            if name == "КТ 6024БС (125А)":
                new_rows.append(dict(KT6032BS_ROW))
                inserted_6032bs = True

        if not inserted_6032bs:
            for i, row in enumerate(new_rows):
                if row["sku_name"] == "КТ 6024БС (125А)":
                    new_rows.insert(i + 1, dict(KT6032BS_ROW))
                    break

        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(new_rows)
        self.stdout.write(f"  Pricelist CSV updated ({len(new_rows)} rows)")

    def _set_featured(self) -> None:
        ProductGroup.objects.filter(is_featured=True).update(is_featured=False)
        qs = ProductGroup.objects.filter(
            is_active=True,
            product_type="KT",
            series_code__in=FEATURED_SERIES,
        )
        count = qs.update(is_featured=True)
        self.stdout.write(f"  Featured (hits): {count} cards — series {', '.join(FEATURED_SERIES)}")

    def _rotate_images(self) -> None:
        try:
            from PIL import Image
        except ImportError:
            self.stdout.write(self.style.WARNING("  Pillow not installed — skip image rotation"))
            return

        tovar_dir = Path(__file__).resolve().parents[5] / "frontend" / "public" / "tovar"
        if not tovar_dir.is_dir():
            tovar_dir = Path("/app/frontend/public/tovar")
        if not tovar_dir.is_dir():
            self.stdout.write(self.style.WARNING(f"  tovar dir not found: {tovar_dir}"))
            return

        rotated = 0
        for filename in ROTATE_IMAGES:
            path = tovar_dir / filename
            if not path.is_file():
                self.stdout.write(self.style.WARNING(f"  missing image: {filename}"))
                continue
            with Image.open(path) as img:
                if img.width >= img.height:
                    continue
                img.transpose(Image.Transpose.ROTATE_270).save(path, quality=92)
                rotated += 1
        self.stdout.write(f"  Rotated {rotated} product photos to landscape")
