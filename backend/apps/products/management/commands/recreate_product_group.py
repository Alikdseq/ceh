"""
Recreate a product group (same slug/URL) without broken ProductImage rows.

Use when admin change page returns 500 due to orphan media in DB.
"""
from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.products.models import ProductGroup, ProductImage, ProductSpec, ProductVariant
from apps.products.product_media import image_file_exists
from apps.products.utils import invalidate_catalog_cache


def _snapshot_group(group: ProductGroup) -> dict:
    return {
        "category_id": group.category_id,
        "name": group.name,
        "slug": group.slug,
        "short_description": group.short_description,
        "full_description": group.full_description,
        "series_code": group.series_code,
        "product_type": group.product_type,
        "nominal_current_a": group.nominal_current_a,
        "nominal_voltage_v": group.nominal_voltage_v,
        "poles": group.poles,
        "application_category": group.application_category,
        "designation_structure": group.designation_structure,
        "honest_sign": group.honest_sign,
        "meta_title": group.meta_title,
        "meta_description": group.meta_description,
        "h1": group.h1,
        "is_active": group.is_active,
        "is_featured": group.is_featured,
        "sort_order": group.sort_order,
        "image_rotation": getattr(group, "image_rotation", 0) or 0,
    }


def _snapshot_variants(group: ProductGroup) -> list[dict]:
    rows = []
    for v in group.variants.order_by("id"):
        rows.append(
            {
                "sku_code": v.sku_code,
                "slug": v.slug,
                "execution": v.execution,
                "coil_type": v.coil_type,
                "coil_voltage_v": v.coil_voltage_v,
                "aux_contacts": v.aux_contacts,
                "price": v.price,
                "price_valid_from": v.price_valid_from,
                "weight_net_kg": v.weight_net_kg,
                "weight_gross_kg": v.weight_gross_kg,
                "dimensions": v.dimensions,
                "stock_status": v.stock_status,
                "is_default": v.is_default,
                "is_active": v.is_active,
            }
        )
    return rows


def _snapshot_specs(group: ProductGroup) -> list[dict]:
    return [
        {
            "spec_key": s.spec_key,
            "spec_value": s.spec_value,
            "spec_unit": s.spec_unit,
            "filterable": s.filterable,
            "sort_order": s.sort_order,
        }
        for s in group.specs.order_by("sort_order", "spec_key")
    ]


def recreate_product_group(
    group: ProductGroup,
    *,
    copy_valid_images: bool = False,
    skip_related: bool = False,
) -> ProductGroup:
    data = _snapshot_group(group)
    variants = _snapshot_variants(group)
    specs = _snapshot_specs(group)
    related_ids = (
        [] if skip_related else list(group.related_groups.values_list("pk", flat=True))
    )

    valid_images = []
    if copy_valid_images:
        for img in group.images.all():
            if img.image.name and image_file_exists(img.image):
                valid_images.append(
                    {
                        "image_name": img.image.name,
                        "alt": img.alt,
                        "sort_order": img.sort_order,
                        "is_primary": img.is_primary,
                    }
                )

    old_pk = group.pk
    old_slug = group.slug

    with transaction.atomic():
        group.delete()

        new_group = ProductGroup.objects.create(**data)

        for row in variants:
            ProductVariant.objects.create(group=new_group, **row)

        for row in specs:
            ProductSpec.objects.create(group=new_group, **row)

        if related_ids:
            new_group.related_groups.set(
                [pk for pk in related_ids if pk != old_pk],
            )

        for img_row in valid_images:
            ProductImage.objects.create(
                group=new_group,
                image=img_row["image_name"],
                alt=img_row["alt"],
                sort_order=img_row["sort_order"],
                is_primary=img_row["is_primary"],
            )

    invalidate_catalog_cache()
    return new_group


class Command(BaseCommand):
    help = "Delete and recreate a product card with the same slug (fixes broken admin/media state)"

    def add_arguments(self, parser):
        parser.add_argument("--pk", type=int, help="ProductGroup id (e.g. 48)")
        parser.add_argument("--slug", type=str, help="ProductGroup slug")
        parser.add_argument(
            "--name-contains",
            type=str,
            default="",
            help="Match active groups whose name contains this text (e.g. КТП6623)",
        )
        parser.add_argument(
            "--copy-images",
            action="store_true",
            help="Copy ProductImage rows only if files exist on disk",
        )
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        qs = ProductGroup.objects.all()
        if options["pk"]:
            qs = qs.filter(pk=options["pk"])
        elif options["slug"]:
            qs = qs.filter(slug=options["slug"])
        elif options["name_contains"]:
            qs = qs.filter(name__icontains=options["name_contains"])
        else:
            raise CommandError("Specify --pk, --slug, or --name-contains")

        groups = list(qs)
        if not groups:
            raise CommandError("No product groups matched")
        if len(groups) > 1:
            self.stdout.write("Multiple matches:")
            for g in groups:
                self.stdout.write(f"  pk={g.pk} slug={g.slug} name={g.name}")
            raise CommandError("Narrow the query (use --pk or --slug)")

        group = groups[0]
        self.stdout.write(
            f"Target: pk={group.pk} slug={group.slug} name={group.name!r} "
            f"variants={group.variants.count()} images={group.images.count()}"
        )

        if options["dry_run"]:
            self.stdout.write(self.style.WARNING("Dry run — no changes"))
            return

        old_pk = group.pk
        new_group = recreate_product_group(group, copy_valid_images=options["copy_images"])
        self.stdout.write(
            self.style.SUCCESS(
                f"Recreated: old pk={old_pk} → new pk={new_group.pk} "
                f"slug={new_group.slug} (URL unchanged). "
                f"Admin: /manage/products/productgroup/{new_group.pk}/change/"
            )
        )
