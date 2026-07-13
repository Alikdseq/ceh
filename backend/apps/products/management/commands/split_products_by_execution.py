from django.core.management.base import BaseCommand
from django.db import transaction

from apps.products.models import ProductGroup, ProductImage, ProductSpec, ProductVariant
from apps.products.services.catalog_parser import build_group_name, build_group_slug
from apps.products.utils import invalidate_catalog_cache

CONTACTOR_TYPES = ("KT", "KTP", "KTE")


def _copy_images(source: ProductGroup, target: ProductGroup) -> int:
    copied = 0
    for img in source.images.all():
        _, created = ProductImage.objects.get_or_create(
            group=target,
            image=img.image,
            defaults={
                "alt": img.alt,
                "sort_order": img.sort_order,
                "is_primary": img.is_primary,
            },
        )
        if created:
            copied += 1
    return copied


def _copy_specs(source: ProductGroup, target: ProductGroup) -> int:
    copied = 0
    for spec in source.specs.all():
        _, created = ProductSpec.objects.update_or_create(
            group=target,
            spec_key=spec.spec_key,
            defaults={
                "spec_value": spec.spec_value,
                "spec_unit": spec.spec_unit,
                "filterable": spec.filterable,
                "sort_order": spec.sort_order,
            },
        )
        if created:
            copied += 1
    return copied


def _group_fields(source: ProductGroup, execution: str, category) -> dict:
    catalog_name = build_group_name(
        source.product_type,
        source.series_code,
        source.nominal_current_a,
        execution,
    ) or source.name
    return {
        "category": category,
        "name": catalog_name,
        "short_description": source.short_description,
        "full_description": source.full_description,
        "series_code": source.series_code,
        "product_type": source.product_type,
        "nominal_current_a": source.nominal_current_a,
        "nominal_voltage_v": source.nominal_voltage_v,
        "poles": source.poles,
        "application_category": source.application_category,
        "designation_structure": source.designation_structure,
        "honest_sign": source.honest_sign,
        "meta_title": source.meta_title,
        "meta_description": source.meta_description,
        "h1": catalog_name,
        "is_active": True,
        "is_featured": source.is_featured,
        "sort_order": source.sort_order,
    }


class Command(BaseCommand):
    help = "Split product groups by execution (Б/БС/С) into separate catalog cards"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report planned splits without writing",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        split_count = 0
        renamed_count = 0
        images_copied = 0

        groups = (
            ProductGroup.objects.filter(is_active=True, product_type__in=CONTACTOR_TYPES)
            .prefetch_related("variants", "images", "specs")
            .select_related("category")
        )

        for group in groups:
            executions = sorted(
                {
                    ex
                    for ex in group.variants.filter(is_active=True).values_list("execution", flat=True)
                    if ex and ex != "NONE"
                }
            )
            if not executions:
                continue

            if len(executions) == 1:
                execution = executions[0]
                new_slug = build_group_slug(
                    group.product_type,
                    group.series_code,
                    group.nominal_current_a,
                    execution,
                )
                if group.slug == new_slug:
                    continue
                if ProductGroup.objects.filter(slug=new_slug).exclude(pk=group.pk).exists():
                    self.stdout.write(
                        self.style.WARNING(f"Skip rename {group.slug} → {new_slug} (target exists)")
                    )
                    continue
                if dry_run:
                    self.stdout.write(f"[dry-run] rename {group.slug} → {new_slug} ({execution})")
                else:
                    group.slug = new_slug
                    group.name = build_group_name(
                        group.product_type,
                        group.series_code,
                        group.nominal_current_a,
                        execution,
                    )
                    if not group.h1:
                        group.h1 = group.name
                    group.save(update_fields=["slug", "name", "h1"])
                renamed_count += 1
                continue

            self.stdout.write(f"Split {group.slug}: {', '.join(executions)}")
            split_count += 1

            for execution in executions:
                new_slug = build_group_slug(
                    group.product_type,
                    group.series_code,
                    group.nominal_current_a,
                    execution,
                )
                if dry_run:
                    count = group.variants.filter(is_active=True, execution=execution).count()
                    self.stdout.write(f"  → {new_slug} ({execution}): {count} variants")
                    continue

                target, created = ProductGroup.objects.update_or_create(
                    slug=new_slug,
                    defaults=_group_fields(group, execution, group.category),
                )
                if created:
                    images_copied += _copy_images(group, target)
                    _copy_specs(group, target)
                else:
                    images_copied += _copy_images(group, target)

                moved = ProductVariant.objects.filter(
                    group=group,
                    is_active=True,
                    execution=execution,
                ).update(group=target)
                self.stdout.write(f"  {new_slug}: {moved} variants")

                if not target.variants.filter(is_default=True, is_active=True).exists():
                    first = target.variants.filter(is_active=True).order_by("price", "sku_code").first()
                    if first:
                        target.variants.update(is_default=False)
                        first.is_default = True
                        first.save(update_fields=["is_default"])

            if not dry_run:
                if not group.variants.filter(is_active=True).exists():
                    group.is_active = False
                    group.save(update_fields=["is_active"])
                    self.stdout.write(f"  deactivated empty group {group.slug}")

        if not dry_run:
            invalidate_catalog_cache()

        self.stdout.write(
            self.style.SUCCESS(
                f"Done: {split_count} groups split, {renamed_count} renamed, {images_copied} images copied"
            )
        )
