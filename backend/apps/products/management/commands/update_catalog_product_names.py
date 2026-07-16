from django.core.management.base import BaseCommand
from django.db import transaction

from apps.products.models import ProductGroup
from apps.products.services.catalog_parser import build_catalog_display_name, strip_climate_suffix
from apps.products.utils import invalidate_catalog_cache


class Command(BaseCommand):
    help = "Привести названия карточек к формату КТ6012Б (без -У3)"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")

    @transaction.atomic
    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        updated = 0

        for group in ProductGroup.objects.filter(is_active=True).prefetch_related("variants"):
            new_name = build_catalog_display_name(group)
            compact = strip_climate_suffix(group.name.replace(" ", ""))
            if not new_name:
                new_name = compact
            elif compact and len(compact) <= len(new_name) + 2:
                new_name = compact
            if not new_name or new_name == group.name:
                continue
            self.stdout.write(f"  {group.slug}: {group.name!r} → {new_name!r}")
            if not dry_run:
                group.name = new_name
                if not group.h1 or "исполнение" in group.h1.lower() or group.h1 == group.name:
                    group.h1 = new_name
                group.save(update_fields=["name", "h1"])
            updated += 1

        if not dry_run:
            invalidate_catalog_cache()

        self.stdout.write(self.style.SUCCESS(f"Updated {updated} product names"))
