"""Set image_rotation for the agreed KT/KTP photo list (default 270°)."""
from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.products.catalog_image_rotation import (
    LISTED_IMAGE_ROTATION_DEGREES,
    should_rotate_product_group,
)
from apps.products.models import ProductGroup
from apps.products.utils import invalidate_catalog_cache


class Command(BaseCommand):
    help = "Apply listed catalog photo rotation (image_rotation) to matching product groups"

    def add_arguments(self, parser):
        parser.add_argument(
            "--degrees",
            type=int,
            default=LISTED_IMAGE_ROTATION_DEGREES,
            help=f"Rotation angle (default {LISTED_IMAGE_ROTATION_DEGREES})",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print matches without saving",
        )

    def handle(self, *args, **options):
        degrees = int(options["degrees"]) % 360
        dry_run = options["dry_run"]
        updated = 0
        matched = 0

        qs = ProductGroup.objects.filter(is_active=True).prefetch_related("variants")
        for group in qs.iterator():
            if not should_rotate_product_group(group):
                continue
            matched += 1
            if group.image_rotation == degrees:
                continue
            self.stdout.write(f"  {group.slug}: {group.image_rotation}° → {degrees}°")
            if not dry_run:
                group.image_rotation = degrees
                group.save(update_fields=["image_rotation", "updated_at"])
            updated += 1

        if not dry_run and updated:
            invalidate_catalog_cache()

        self.stdout.write(
            self.style.SUCCESS(
                f"Matched {matched} groups, {'would update' if dry_run else 'updated'} {updated} "
                f"to {degrees}°"
            )
        )
