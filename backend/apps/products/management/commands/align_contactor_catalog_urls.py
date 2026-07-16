"""Align product group slug and nominal current with catalog (fixes wrong pricelist URLs)."""
from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.products.models import ProductGroup
from apps.products.services.catalog_parser import build_group_slug
from apps.products.utils import invalidate_catalog_cache

# Series where pricelist had wrong nominal_current_a (catalog truth: 250А for 6634).
SERIES_NOMINAL_A: dict[tuple[str, str], int] = {
    ("KT", "6634"): 250,
    ("KTP", "6634"): 250,
}


def _primary_execution(group: ProductGroup) -> str | None:
    ex = (
        group.variants.filter(is_active=True)
        .exclude(execution="NONE")
        .values_list("execution", flat=True)
        .first()
    )
    return ex or None


def expected_slug(group: ProductGroup) -> str | None:
    if group.product_type not in ("KT", "KTP", "KTE") or not group.series_code:
        return None
    return build_group_slug(
        group.product_type,
        group.series_code,
        group.nominal_current_a,
        _primary_execution(group),
    )


class Command(BaseCommand):
    help = "Fix nominal_current_a and slug for contactors (canonical URLs like kontaktor-kt-6634-250a-s)"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        dry = options["dry_run"]
        updated = 0

        with transaction.atomic():
            for group in ProductGroup.objects.filter(
                product_type__in=("KT", "KTP"),
                is_active=True,
            ).prefetch_related("variants"):
                key = (group.product_type, group.series_code)
                nominal_fix = SERIES_NOMINAL_A.get(key)
                fields: list[str] = []

                if nominal_fix is not None and group.nominal_current_a != nominal_fix:
                    self.stdout.write(
                        f"  {group.slug}: nominal {group.nominal_current_a} → {nominal_fix}"
                    )
                    if not dry:
                        group.nominal_current_a = nominal_fix
                        fields.append("nominal_current_a")

                exp = expected_slug(group)
                if exp and group.slug != exp:
                    collision = (
                        ProductGroup.objects.filter(slug=exp).exclude(pk=group.pk).exists()
                    )
                    if collision:
                        self.stdout.write(
                            self.style.WARNING(
                                f"  skip slug {group.slug} → {exp} (slug taken)"
                            )
                        )
                    else:
                        self.stdout.write(f"  {group.slug} → slug {exp}")
                        if not dry:
                            group.slug = exp
                            fields.append("slug")

                if fields and not dry:
                    group.save(update_fields=[*fields, "updated_at"])
                    updated += 1

            if dry:
                transaction.set_rollback(True)

        if not dry and updated:
            invalidate_catalog_cache()
        self.stdout.write(self.style.SUCCESS(f"Updated {updated} product group(s)"))
