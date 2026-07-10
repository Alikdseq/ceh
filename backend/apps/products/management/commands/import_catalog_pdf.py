from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify

from apps.products.models import Category, ProductGroup, ProductSpec, ProductVariant
from apps.products.services.catalog_parser import (
    build_group_name,
    build_group_slug,
    category_slug_for_group,
    group_key_from_page,
    parse_model_code,
    resolve_catalog_pages,
    sku_to_slug,
)


class Command(BaseCommand):
    help = "Import ProductGroup from catalog PDF (STEP-032)"

    def add_arguments(self, parser):
        parser.add_argument("pdf_path", type=str, help="Path to catalog PDF")
        parser.add_argument("--clear-products", action="store_true", help="Delete all products first")

    @transaction.atomic
    def handle(self, *args, **options):
        path = Path(options["pdf_path"])
        if not path.exists():
            matches = list(Path(".").glob(str(path)))
            if matches:
                path = matches[0]
            elif path.parent.exists():
                extract = path.parent / "catalog_extract.txt"
                if extract.exists():
                    path = extract
                else:
                    raise CommandError(f"PDF not found: {options['pdf_path']}")
            else:
                extract = Path("data/source/catalog_extract.txt")
                if extract.exists():
                    path = extract
                else:
                    raise CommandError(f"PDF not found: {options['pdf_path']}")

        if options["clear_products"]:
            ProductVariant.objects.all().delete()
            ProductGroup.objects.all().delete()
            ProductSpec.objects.all().delete()
            self.stdout.write("Cleared existing products")

        pages = resolve_catalog_pages(path)
        groups_created = 0
        variants_created = 0
        seen_keys: set[tuple] = set()

        for page in pages:
            if not page.models:
                continue
            key = group_key_from_page(page)
            if key in seen_keys:
                continue
            seen_keys.add(key)

            series, current, product_type = key
            first_parsed = parse_model_code(page.models[0], page.specs)
            execution = first_parsed.execution
            cat_slug = category_slug_for_group(product_type, series, execution)
            category = Category.objects.filter(slug=cat_slug).first()
            if not category:
                category = Category.objects.filter(slug="kontaktory-kt").first()
            if not category:
                raise CommandError(f"Category not found: {cat_slug}. Run import_categories first.")

            name = build_group_name(product_type, series, current)
            slug = build_group_slug(product_type, series, current)

            group, g_created = ProductGroup.objects.update_or_create(
                slug=slug,
                defaults={
                    "category": category,
                    "name": name,
                    "short_description": page.purpose[:500] if page.purpose else "",
                    "full_description": page.purpose,
                    "series_code": series,
                    "product_type": product_type,
                    "nominal_current_a": current,
                    "nominal_voltage_v": 380,
                    "poles": self._parse_int_spec(page.specs.get("Число полюсов")),
                    "application_category": page.specs.get("Категория применения", "AC-3, AC-4"),
                    "honest_sign": page.honest_sign,
                    "is_active": True,
                },
            )
            if g_created:
                groups_created += 1

            self._upsert_specs(group, page.specs)

            for i, model_raw in enumerate(page.models):
                parsed = parse_model_code(model_raw, page.specs)
                sku = model_raw.replace(" ", "")
                variant_slug = sku_to_slug(sku)
                coil_type = "DC" if product_type == "KTP" else "AC"
                default_coil = (
                    parsed.coil_voltages_dc[0] if parsed.coil_voltages_dc
                    else (parsed.coil_voltages_ac[0] if parsed.coil_voltages_ac else None)
                )
                _, v_created = ProductVariant.objects.update_or_create(
                    sku_code=sku,
                    defaults={
                        "group": group,
                        "slug": variant_slug,
                        "execution": parsed.execution if parsed.execution != "NONE" else "B",
                        "coil_type": coil_type,
                        "coil_voltage_v": default_coil,
                        "is_default": i == 0,
                        "is_active": True,
                    },
                )
                if v_created:
                    variants_created += 1

        self.stdout.write(self.style.SUCCESS(
            f"PDF import: {len(pages)} pages, {groups_created} new groups, "
            f"{variants_created} new variants, {ProductGroup.objects.count()} total groups"
        ))

    def _parse_int_spec(self, value: str | None) -> int | None:
        if not value:
            return None
        import re
        m = re.search(r"(\d+)", value)
        return int(m.group(1)) if m else None

    def _upsert_specs(self, group: ProductGroup, specs: dict):
        mapping = {
            "Номинальная сила тока": ("nominal_current", "А", True),
            "Номинальное напряжение": ("nominal_voltage", "В", True),
            "Номинальная частота": ("frequency", "Гц", False),
            "Число полюсов": ("poles", "", True),
            "Категория применения": ("application_category", "", True),
        }
        for label, (key, unit, filterable) in mapping.items():
            if label in specs:
                val = specs[label].replace("А", "").replace("В", "").replace("Гц", "").strip()
                ProductSpec.objects.update_or_create(
                    group=group,
                    spec_key=key,
                    defaults={"spec_value": val.split()[0] if val else specs[label], "spec_unit": unit, "filterable": filterable},
                )
