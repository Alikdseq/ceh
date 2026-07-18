import csv
from datetime import date
from decimal import Decimal
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify

from apps.core.paths import resolve_data_file
from apps.products.models import Category, ProductGroup, ProductVariant
from apps.products.services.catalog_parser import (
    build_group_name,
    build_group_slug,
    normalize_pricelist_name,
    pricelist_category_slug,
    sku_to_slug,
)


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

        zero_price = ProductVariant.objects.filter(price=0, is_active=True).count()
        total = ProductVariant.objects.filter(is_active=True).count()
        self.stdout.write(self.style.SUCCESS(
            f"Pricelist: +{created_groups} groups, +{created_variants} variants, "
            f"{updated_prices} prices updated, {total} total variants, {zero_price} without price"
        ))

        # Copy price within group for sibling executions (Б/БС from same pricelist row)
        propagated = 0
        for group in ProductGroup.objects.filter(variants__price=0).distinct():
            ref = group.variants.filter(price__gt=0).order_by("is_default").first()
            if ref:
                propagated += group.variants.filter(price=0).update(
                    price=ref.price, price_valid_from=ref.price_valid_from,
                )
        if propagated:
            self.stdout.write(f"  Propagated price to {propagated} sibling variants")

        coil_propagated = self._propagate_prices_to_coil_variants()
        if coil_propagated:
            self.stdout.write(f"  Propagated price to {coil_propagated} coil variants")

        call_command("import_price_list", str(path))
        self.stdout.write(self.style.SUCCESS("  Public /pricelist table synced"))

    def _propagate_prices_to_coil_variants(self) -> int:
        """Apply base SKU price to variants like КТ6012Б-У3-36V."""
        updated = 0
        for variant in ProductVariant.objects.filter(is_active=True, price__gt=0).iterator():
            count = ProductVariant.objects.filter(
                is_active=True,
                sku_code__startswith=f"{variant.sku_code}-",
                price=0,
            ).update(price=variant.price, price_valid_from=variant.price_valid_from)
            updated += count
        return updated

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

        if ptype in ("KT", "KTP", "KTE") and series:
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

        if ptype in ("KT", "KTP", "KTE") and series:
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
        if existing:
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
