import csv
from datetime import date
from decimal import Decimal
from pathlib import Path
import re

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify

from apps.core.paths import resolve_data_file
from apps.products.models import Category, ProductGroup, ProductVariant
from apps.products.services.catalog_parser import (
    build_group_name,
    build_group_slug,
    format_cam_display_name,
    normalize_pricelist_name,
    pricelist_category_slug,
    sku_to_slug,
)
from apps.products.services.pricing import apply_group_price, sync_all_variant_prices


class Command(BaseCommand):
    help = "Import prices and variants from CSV pricelist (STEP-033)"

    def add_arguments(self, parser):
        parser.add_argument("csv_path", type=str, help="Path to pricelist.csv")

    @transaction.atomic
    def handle(self, *args, **options):
        path = resolve_data_file(options["csv_path"])
        if not path.exists():
            raise CommandError(
                f"File not found: {options['csv_path']} "
                f"(also checked /data/pricelist.csv)"
            )

        created_groups = 0
        created_variants = 0
        updated_prices = 0
        today = date.today()

        with path.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                parsed = normalize_pricelist_name(row["sku_name"])
                price = Decimal(row["price_rub"].replace(" ", "").replace(",", "."))
                notes = row.get("notes", "")

                group, g_created = self._find_or_create_group(parsed, row, notes)
                if g_created:
                    created_groups += 1

                sku = parsed["sku_code"]
                variant_slug = parsed["slug"] or sku_to_slug(sku)
                has_default = group.variants.filter(is_default=True).exists()

                variant, v_created = ProductVariant.objects.update_or_create(
                    sku_code=sku,
                    defaults={
                        "group": group,
                        "slug": variant_slug,
                        "execution": parsed["execution"] if parsed["execution"] != "NONE" else "NONE",
                        "coil_type": self._coil_type(parsed["product_type"]),
                        "price": price,
                        "price_valid_from": today,
                        "is_active": True,
                        "is_default": False,
                    },
                )
                if v_created:
                    created_variants += 1
                    if not has_default:
                        variant.is_default = True
                        variant.save(update_fields=["is_default"])
                else:
                    updated_prices += 1

                apply_group_price(group, price, today)

        stats = sync_all_variant_prices()
        zero_price = ProductVariant.objects.filter(price=0, is_active=True).count()
        total = ProductVariant.objects.filter(is_active=True).count()
        self.stdout.write(self.style.SUCCESS(
            f"Pricelist: +{created_groups} groups, +{created_variants} variants, "
            f"{updated_prices} prices updated, {total} total variants, {zero_price} without price"
        ))
        if stats["within_group"] or stats["by_sku_prefix"]:
            self.stdout.write(
                f"  Price sync: {stats['within_group']} within group, "
                f"{stats['by_sku_prefix']} by SKU prefix"
            )

        call_command("import_price_list", str(path))
        self.stdout.write(self.style.SUCCESS("  Public /pricelist table synced"))

    def _coil_type(self, product_type: str) -> str:
        if product_type == "KTP":
            return "DC"
        if product_type in ("KT",):
            return "AC"
        return "NONE"

    def _find_or_create_group(self, parsed: dict, row: dict, notes: str) -> tuple[ProductGroup, bool]:
        series = parsed["series_code"]
        current = parsed.get("nominal_current_a") or (
            int(row["nominal_current_a"]) if row.get("nominal_current_a") else None
        )
        ptype = parsed["product_type"]

        if ptype in ("KT", "KTP") and series:
            execution = parsed.get("execution")
            exec_key = execution if execution and execution != "NONE" else None
            slug = build_group_slug(ptype, series, current, exec_key)
            group = ProductGroup.objects.filter(slug=slug).first()
            if group:
                return group, False

        if series and ptype in ("KT", "KTP"):
            group = ProductGroup.objects.filter(
                series_code=series,
                product_type=ptype,
                nominal_current_a=current,
            ).first()
            if group:
                return group, False

        cat_slug = pricelist_category_slug(parsed, notes)
        category = Category.objects.filter(slug=cat_slug).first()
        if not category:
            category = Category.objects.first()
            if not category:
                raise CommandError("No categories in DB. Run import_categories first.")

        if ptype in ("KT", "KTP") and series:
            execution = parsed.get("execution")
            exec_key = execution if execution and execution != "NONE" else None
            name = build_group_name(ptype, series, current, exec_key)
            slug = build_group_slug(ptype, series, current, exec_key)
        else:
            name = parsed["name"]
            slug = slugify(name, allow_unicode=False)[:255]
            if not slug:
                slug = slugify(name, allow_unicode=True)[:255]
            if not slug:
                slug = slugify(parsed["sku_code"], allow_unicode=True)[:255]

        existing = ProductGroup.objects.filter(slug=slug).first()
        if not existing and ptype == "KTE":
            series_m = re.search(r"(\d{2}-\d+)", name)
            suffix = name.split()[-1].upper() if name.split() else ""
            if series_m and suffix:
                existing = (
                    ProductGroup.objects.filter(product_type="KTE", name__icontains=series_m.group(1))
                    .filter(name__icontains=suffix[:4])
                    .first()
                )
        if not existing and ptype == "CAM":
            cam_label = format_cam_display_name(name, parsed.get("sku_code", ""))
            if cam_label:
                existing = ProductGroup.objects.filter(
                    product_type="CAM",
                    name__icontains=cam_label,
                ).first()

        if existing:
            if existing.name != name:
                existing.name = name
                if not existing.h1 or existing.h1 == existing.name:
                    existing.h1 = name
                existing.save(update_fields=["name", "h1"])
            return existing, False

        group = ProductGroup.objects.create(
            category=category,
            name=name,
            slug=slug,
            series_code=series or slug[:20],
            product_type=ptype if ptype in dict(ProductGroup.ProductType.choices) else "OTHER",
            nominal_current_a=current,
            is_active=True,
        )
        return group, True
