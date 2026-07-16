"""Remove ProductImage rows whose files are missing from storage (fixes admin 500)."""
from __future__ import annotations

from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand

from apps.products.models import ProductImage
from apps.products.utils import invalidate_catalog_cache


class Command(BaseCommand):
    help = "Delete product image DB rows when media file is missing on disk"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        removed = 0
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
            if not dry_run:
                img.delete()
            removed += 1
        if not dry_run and removed:
            invalidate_catalog_cache()
        self.stdout.write(
            self.style.SUCCESS(
                f"{'Would remove' if dry_run else 'Removed'} {removed} broken image record(s)"
            )
        )
