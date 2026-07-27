import csv
from decimal import Decimal
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.core.paths import resolve_data_file
from apps.content.models import PriceListItem, PriceListSection
from apps.content.services.pricelist import merge_duplicate_pricelist_sections


class Command(BaseCommand):
    help = "Import public price list table from CSV (category, sku_name, price_rub, ...)"

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_path",
            nargs="?",
            default="data/pricelist.csv",
            type=str,
            help="Path to pricelist CSV",
        )
        parser.add_argument(
            "--replace",
            action="store_true",
            help="Deactivate items not present in CSV",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        path = resolve_data_file(options["csv_path"])
        if not path.is_file():
            raise CommandError(
                f"File not found: {options['csv_path']} "
                f"(also checked /data/pricelist.csv)"
            )

        seen_ids: set[int] = set()
        sections_cache: dict[str, PriceListSection] = {}
        created_items = updated_items = 0

        merged = merge_duplicate_pricelist_sections()
        if merged:
            self.stdout.write(f"Merged {merged} duplicate pricelist section(s)")

        with path.open(encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for index, row in enumerate(reader):
                section_name = (row.get("category") or "Прочее").strip()
                section = sections_cache.get(section_name)
                if not section:
                    existing = (
                        PriceListSection.objects.filter(name=section_name, is_active=True)
                        .order_by("sort_order", "pk")
                        .first()
                    )
                    if existing:
                        section = existing
                    else:
                        section = PriceListSection.objects.create(
                            name=section_name,
                            sort_order=len(sections_cache),
                            is_active=True,
                        )
                    sections_cache[section_name] = section

                price_raw = (row.get("price_rub") or "0").replace(" ", "").replace(",", ".")
                current_raw = row.get("nominal_current_a") or ""
                current = int(current_raw) if str(current_raw).strip().isdigit() else None

                item, created = PriceListItem.objects.update_or_create(
                    section=section,
                    name=row["sku_name"].strip(),
                    defaults={
                        "price": Decimal(price_raw),
                        "nominal_current_a": current,
                        "product_type": (row.get("product_type") or "").strip(),
                        "notes": (row.get("notes") or "").strip(),
                        "sort_order": index,
                        "is_active": True,
                    },
                )
                seen_ids.add(item.pk)
                if created:
                    created_items += 1
                else:
                    updated_items += 1

        deactivated = 0
        if options["replace"]:
            deactivated = PriceListItem.objects.exclude(pk__in=seen_ids).update(is_active=False)

        merged_after = merge_duplicate_pricelist_sections()
        if merged_after:
            self.stdout.write(f"Merged {merged_after} duplicate pricelist section(s) after import")

        self.stdout.write(
            self.style.SUCCESS(
                f"Price list: {len(sections_cache)} sections, "
                f"+{created_items} items, {updated_items} updated"
                + (f", {deactivated} deactivated" if deactivated else "")
            )
        )
