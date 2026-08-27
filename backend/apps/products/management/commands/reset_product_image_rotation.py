"""Reset product card photo rotation to 0 (show images as uploaded)."""

from django.core.management.base import BaseCommand

from apps.products.models import ProductGroup
from apps.products.utils import invalidate_catalog_cache


class Command(BaseCommand):
    help = "Set image_rotation=0 for all product groups (fixes auto-rotated catalog photos)"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        qs = ProductGroup.objects.exclude(image_rotation=0)
        count = qs.count()
        if options["dry_run"]:
            for group in qs.iterator():
                self.stdout.write(f"  {group.slug}: {group.image_rotation}° → 0°")
            self.stdout.write(self.style.SUCCESS(f"Would reset {count} product group(s)"))
            return

        updated = qs.update(image_rotation=0)
        if updated:
            invalidate_catalog_cache()
        self.stdout.write(self.style.SUCCESS(f"Reset image_rotation for {updated} product group(s)"))
