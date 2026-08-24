"""Create ProductImage rows for groups that use static /tovar/ photos on the site."""

from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.products.catalog_static_photos import catalog_tovar_file
from apps.products.models import ProductGroup, ProductImage
from apps.products.static_product_images import (
    resolve_static_product_image_for_group,
    static_url_basename,
)
from apps.products.utils import invalidate_catalog_cache


class Command(BaseCommand):
    help = (
        "Link static catalog photos to ProductGroup rows so they appear in admin "
        "(editable/deletable). Safe to run repeatedly."
    )

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--slug", help="Only process one product group slug")

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        slug_filter = options.get("slug")

        qs = ProductGroup.objects.filter(is_active=True).order_by("pk")
        if slug_filter:
            qs = qs.filter(slug=slug_filter)

        created = 0
        skipped_has_images = 0
        skipped_no_static = 0
        skipped_no_file = 0

        for group in qs.iterator():
            if group.images.exists():
                skipped_has_images += 1
                continue

            static_url = resolve_static_product_image_for_group(group)
            if not static_url:
                skipped_no_static += 1
                continue

            basename = static_url_basename(static_url)
            if not basename or catalog_tovar_file(basename) is None:
                skipped_no_file += 1
                continue

            image_name = f"products/{basename}"
            if dry_run:
                self.stdout.write(f"  would link {group.slug}: {image_name}")
                created += 1
                continue

            ProductImage.objects.create(
                group=group,
                image=image_name,
                alt=group.name,
                sort_order=0,
                is_primary=True,
            )
            created += 1

        if not dry_run and created:
            invalidate_catalog_cache()

        self.stdout.write(
            self.style.SUCCESS(
                f"Done: linked {created}, "
                f"skipped (already has CMS) {skipped_has_images}, "
                f"no static match {skipped_no_static}, "
                f"static without /tovar/ file {skipped_no_file}"
            )
        )
