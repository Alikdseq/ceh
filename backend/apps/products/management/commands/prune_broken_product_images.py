"""Remove ProductImage rows whose files are missing from storage (fixes admin 500)."""
from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.products.product_media import prune_all_broken_product_images
from apps.products.utils import invalidate_catalog_cache


class Command(BaseCommand):
    help = "Delete product image DB rows when media file is missing on disk"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        if options["dry_run"]:
            from django.core.files.storage import default_storage

            from apps.products.models import ProductImage

            count = 0
            for img in ProductImage.objects.select_related("group").iterator():
                name = img.image.name if img.image else ""
                if not name:
                    continue
                try:
                    exists = default_storage.exists(name)
                except OSError:
                    exists = False
                if exists:
                    continue
                self.stdout.write(f"  #{img.pk} {img.group.slug}: {name}")
                count += 1
            self.stdout.write(self.style.SUCCESS(f"Would remove {count} broken image record(s)"))
            return

        removed = prune_all_broken_product_images()
        if removed:
            invalidate_catalog_cache()
        self.stdout.write(self.style.SUCCESS(f"Removed {removed} broken image record(s)"))
