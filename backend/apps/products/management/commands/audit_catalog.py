from pathlib import Path

from django.core.management.base import BaseCommand

from apps.products.models import ProductGroup, ProductVariant
from apps.products.services.catalog_parser import (
    group_key_from_page,
    parse_catalog_text_file,
    parse_model_code,
)


class Command(BaseCommand):
    help = "Audit catalog text source vs database (report only)"

    def add_arguments(self, parser):
        parser.add_argument(
            "text_path",
            nargs="?",
            default="тексткаталога.txt",
            type=str,
        )

    def handle(self, *args, **options):
        repo_root = Path(__file__).resolve().parents[5]
        path = Path(options["text_path"])
        if not path.exists():
            for candidate in [repo_root / "тексткаталога.txt", Path("тексткаталога.txt")]:
                if candidate.exists():
                    path = candidate
                    break

        pages = parse_catalog_text_file(path)
        expected_groups: set[str] = set()
        expected_skus: set[str] = set()

        for page in pages:
            if not page.models:
                continue
            series, current, product_type = group_key_from_page(page)
            from apps.products.services.catalog_parser import build_group_slug

            expected_groups.add(build_group_slug(product_type, series, current))
            for model_raw in page.models:
                parsed = parse_model_code(model_raw, page.specs)
                base_sku = model_raw.replace(" ", "")
                coils = parsed.coil_voltages_dc if product_type == "KTP" else parsed.coil_voltages_ac
                if not coils:
                    expected_skus.add(base_sku)
                else:
                    for coil in coils:
                        expected_skus.add(f"{base_sku}-{coil}V")

        self.stdout.write(f"Source: {path.name}")
        self.stdout.write(f"  Pages parsed: {len(pages)}")
        self.stdout.write(f"  Expected groups: {len(expected_groups)}")
        self.stdout.write(f"  Expected variant SKUs: {len(expected_skus)}")

        db_groups = set(
            ProductGroup.objects.filter(
                product_type__in=("KT", "KTP", "KTE"), is_active=True,
            ).values_list("slug", flat=True)
        )
        db_skus = set(
            ProductVariant.objects.filter(
                is_active=True, group__product_type__in=("KT", "KTP", "KTE"),
            ).values_list("sku_code", flat=True)
        )

        self.stdout.write(f"Database:")
        self.stdout.write(f"  Active groups (KT/KTP/KTE): {len(db_groups)}")
        self.stdout.write(f"  Active variant SKUs: {len(db_skus)}")

        missing_groups = expected_groups - db_groups
        extra_groups = db_groups - expected_groups
        missing_skus = expected_skus - db_skus
        extra_skus = db_skus - expected_skus

        if missing_groups:
            self.stdout.write(self.style.WARNING(f"  Missing groups ({len(missing_groups)}):"))
            for slug in sorted(missing_groups)[:20]:
                self.stdout.write(f"    - {slug}")
            if len(missing_groups) > 20:
                self.stdout.write(f"    … and {len(missing_groups) - 20} more")

        if extra_groups:
            self.stdout.write(self.style.WARNING(f"  Extra groups in DB ({len(extra_groups)}):"))
            for slug in sorted(extra_groups)[:20]:
                self.stdout.write(f"    - {slug}")

        if missing_skus:
            self.stdout.write(self.style.WARNING(f"  Missing SKUs ({len(missing_skus)}):"))
            for sku in sorted(missing_skus)[:15]:
                self.stdout.write(f"    - {sku}")

        if extra_skus:
            self.stdout.write(self.style.WARNING(f"  Extra SKUs in DB ({len(extra_skus)}):"))
            for sku in sorted(extra_skus)[:15]:
                self.stdout.write(f"    - {sku}")

        if not missing_groups and not missing_skus and not extra_groups:
            self.stdout.write(self.style.SUCCESS("Catalog is in sync with text source."))
        else:
            self.stdout.write(
                self.style.NOTICE(
                    "Run: python manage.py sync_catalog --prune  "
                    "then python manage.py audit_catalog"
                )
            )
