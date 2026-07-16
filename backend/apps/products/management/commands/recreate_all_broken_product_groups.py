"""Recreate every product card that has orphan ProductImage rows (missing files)."""
from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.products.management.commands.recreate_product_group import recreate_product_group
from apps.products.models import ProductGroup
from apps.products.product_media import image_file_exists, product_group_ids_with_broken_images
from apps.products.utils import invalidate_catalog_cache


def _restore_related_by_slug(related_by_slug: dict[str, list[str]]) -> None:
    for slug, related_slugs in related_by_slug.items():
        try:
            group = ProductGroup.objects.get(slug=slug)
        except ProductGroup.DoesNotExist:
            continue
        if not related_slugs:
            continue
        peers = ProductGroup.objects.filter(slug__in=related_slugs).exclude(pk=group.pk)
        group.related_groups.set(peers)


class Command(BaseCommand):
    help = (
        "Recreate all product cards with missing image files on disk "
        "(same slug/URL; drops broken photos, keeps valid ones)"
    )

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument(
            "--no-copy-images",
            action="store_true",
            help="Do not re-attach photos that still exist on disk after recreate",
        )

    def handle(self, *args, **options):
        pks = product_group_ids_with_broken_images()
        if not pks:
            self.stdout.write(self.style.SUCCESS("No product groups with broken images"))
            return

        groups = list(
            ProductGroup.objects.filter(pk__in=pks).select_related("category").order_by("pk")
        )
        self.stdout.write(f"Found {len(groups)} product group(s) with broken image record(s):")
        for g in groups:
            broken = sum(
                1 for img in g.images.all() if img.image.name and not image_file_exists(img.image)
            )
            self.stdout.write(
                f"  pk={g.pk} slug={g.slug} name={g.name!r} broken_images≈{broken}"
            )

        if options["dry_run"]:
            self.stdout.write(self.style.WARNING("Dry run — no changes"))
            return

        related_by_slug = {
            g.slug: list(g.related_groups.values_list("slug", flat=True)) for g in groups
        }

        copy_valid = not options["no_copy_images"]
        recreated = 0
        for g in groups:
            old_pk = g.pk
            slug = g.slug
            new_group = recreate_product_group(
                g,
                copy_valid_images=copy_valid,
                skip_related=True,
            )
            recreated += 1
            self.stdout.write(
                f"  OK pk {old_pk} → {new_group.pk} slug={slug}"
            )

        _restore_related_by_slug(related_by_slug)
        invalidate_catalog_cache()
        self.stdout.write(
            self.style.SUCCESS(f"Recreated {recreated} product group(s). Related products re-linked by slug.")
        )
