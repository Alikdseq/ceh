"""Compare catalog variant prices with data/pricelist.csv and optionally fix."""

from __future__ import annotations

import csv
from decimal import Decimal

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from apps.core.paths import resolve_data_file
from apps.products.models import ProductGroup, ProductVariant
from apps.products.services.catalog_parser import normalize_pricelist_name
from apps.products.services.pricing import sync_all_variant_prices


class Command(BaseCommand):
    help = "Audit (and optionally fix) product prices against pricelist.csv"

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_path",
            nargs="?",
            default="data/pricelist.csv",
            type=str,
        )
        parser.add_argument("--fix", action="store_true", help="Re-import pricelist and sync names")
        parser.add_argument("--fail-on-error", action="store_true")

    def handle(self, *args, **options):
        path = resolve_data_file(options["csv_path"])
        if not path.is_file():
            raise CommandError(f"File not found: {options['csv_path']}")

        if options["fix"]:
            call_command("import_pricelist", str(path))
            call_command("update_catalog_product_names")
            call_command("import_price_list", str(path), replace=True)
            call_command("rename_accessories_category")
            stats = sync_all_variant_prices()
            self._clear_kte_honest_sign()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Pricelist re-imported and names synced "
                    f"(price sync: {stats['within_group']} within group, "
                    f"{stats['by_sku_prefix']} by prefix)"
                )
            )
            return

        issues: list[str] = []
        with path.open(encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                parsed = normalize_pricelist_name(row["sku_name"])
                expected = Decimal(row["price_rub"].replace(" ", "").replace(",", "."))
                sku = parsed["sku_code"]
                name = parsed["name"]

                variant = ProductVariant.objects.filter(sku_code=sku, is_active=True).first()
                if not variant:
                    group = ProductGroup.objects.filter(name=name, is_active=True).first()
                    if group:
                        variant = (
                            group.variants.filter(is_active=True).order_by("-is_default").first()
                        )
                if not variant:
                    issues.append(f"No variant for {name!r} (sku={sku})")
                    continue
                if variant.price != expected:
                    issues.append(
                        f"{name}: DB {variant.price} ≠ CSV {expected} (sku={variant.sku_code})"
                    )

        if issues:
            self.stdout.write(self.style.WARNING(f"Found {len(issues)} price mismatch(es):"))
            for line in issues[:40]:
                self.stdout.write(f"  - {line}")
            if len(issues) > 40:
                self.stdout.write(f"  … and {len(issues) - 40} more")
        else:
            self.stdout.write(self.style.SUCCESS("All pricelist rows match catalog prices"))

        unpriced_groups = (
            ProductGroup.objects.filter(is_active=True)
            .exclude(variants__is_active=True, variants__price__gt=0)
            .order_by("name")
        )
        if unpriced_groups.exists():
            self.stdout.write(
                self.style.WARNING(
                    f"{unpriced_groups.count()} active product group(s) without any priced variant:"
                )
            )
            for group in unpriced_groups[:20]:
                self.stdout.write(f"  - {group.name} ({group.slug})")
            if unpriced_groups.count() > 20:
                self.stdout.write(f"  … and {unpriced_groups.count() - 20} more")

        if options["fail_on_error"] and (issues or unpriced_groups.exists()):
            raise CommandError(
                f"{len(issues)} price mismatch(es), "
                f"{unpriced_groups.count()} group(s) without price"
            )

    def _clear_kte_honest_sign(self) -> None:
        updated = ProductGroup.objects.filter(product_type="KTE", honest_sign=True).update(
            honest_sign=False
        )
        if updated:
            self.stdout.write(f"  Cleared honest_sign on {updated} KTE group(s)")
