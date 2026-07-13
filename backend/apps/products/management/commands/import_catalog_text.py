from pathlib import Path
import re

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.products.models import ProductGroup, ProductSpec, ProductVariant
from apps.products.services.catalog_parser import (
    aux_contacts_sku_suffix,
    build_group_name,
    build_group_slug,
    category_slug_for_group,
    group_key_from_page,
    parse_aux_contacts_options,
    parse_aux_contacts_raw,
    parse_catalog_text_file,
    parse_model_code,
    sku_to_slug,
)


class Command(BaseCommand):
    help = "Import ProductGroup from plain-text catalog (тексткаталога.txt)"

    def add_arguments(self, parser):
        parser.add_argument(
            "text_path",
            nargs="?",
            default="тексткаталога.txt",
            type=str,
            help="Path to catalog text file",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report changes without writing to DB",
        )
        parser.add_argument(
            "--prune",
            action="store_true",
            help="Deactivate groups/variants not present in source file",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        path = Path(options["text_path"])
        if not path.exists():
            backend_root = Path(__file__).resolve().parents[4]
            repo_root = backend_root.parent
            for candidate in [
                Path(options["text_path"]),
                repo_root / "тексткаталога.txt",
                backend_root / "тексткаталога.txt",
                Path("тексткаталога.txt"),
                Path("../тексткаталога.txt"),
                Path("data/source/тексткаталога.txt"),
                Path("/data/тексткаталога.txt"),
            ]:
                if candidate.exists():
                    path = candidate
                    break
            else:
                raise CommandError(f"Catalog text not found: {options['text_path']}")

        pages = parse_catalog_text_file(path)
        if not pages:
            raise CommandError(f"No product pages parsed from {path}")

        from apps.products.models import Category

        groups_created = groups_updated = 0
        variants_created = variants_updated = 0
        seen_skus: set[str] = set()
        seen_group_slugs: set[str] = set()
        dry_run = options["dry_run"]

        for page in pages:
            if not page.models:
                continue

            key = group_key_from_page(page)
            series, current, product_type = key
            first_parsed = parse_model_code(page.models[0], page.specs)
            cat_slug = category_slug_for_group(product_type, series, first_parsed.execution)
            category = Category.objects.filter(slug=cat_slug).first()
            if not category:
                category = Category.objects.filter(slug="kontaktory-kt").first()
            if not category:
                raise CommandError(f"Category not found: {cat_slug}. Run import_categories first.")

            group_defaults_base = {
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
            }

            # Group catalog models by execution — separate card per Б/БС/С
            models_by_execution: dict[str, list[str]] = {}
            for model_raw in page.models:
                parsed_model = parse_model_code(model_raw, page.specs)
                exec_key = parsed_model.execution if parsed_model.execution != "NONE" else "B"
                models_by_execution.setdefault(exec_key, []).append(model_raw)

            for execution, models_for_exec in models_by_execution.items():
                exec_slug = build_group_slug(product_type, series, current, execution)
                exec_name = build_group_name(product_type, series, current, execution) or exec_name
                seen_group_slugs.add(exec_slug)

                exec_cat_slug = category_slug_for_group(product_type, series, execution)
                exec_category = Category.objects.filter(slug=exec_cat_slug).first() or category

                group_defaults = {
                    **group_defaults_base,
                    "category": exec_category,
                    "name": exec_name,
                }

                if dry_run:
                    self.stdout.write(f"[dry-run] group {exec_slug} ({execution}): {models_for_exec}")
                    group = ProductGroup.objects.filter(slug=exec_slug).first()
                else:
                    group, g_created = ProductGroup.objects.update_or_create(
                        slug=exec_slug,
                        defaults=group_defaults,
                    )
                    if g_created:
                        groups_created += 1
                    else:
                        groups_updated += 1
                    self._upsert_specs(group, page.specs)

                aux_options = parse_aux_contacts_options(page.specs)
                multi_aux = len(aux_options) > 1
                if not aux_options:
                    aux_options = [""]

                variant_index = 0
                for model_raw in models_for_exec:
                    parsed = parse_model_code(model_raw, page.specs)
                    base_sku = model_raw.replace(" ", "")
                    coil_type = "DC" if product_type == "KTP" else "AC"
                    coils = parsed.coil_voltages_dc if product_type == "KTP" else parsed.coil_voltages_ac
                    if not coils:
                        coils = [None]

                    variant_execution = parsed.execution if parsed.execution != "NONE" else "B"
                    for aux in aux_options:
                        aux_suffix = aux_contacts_sku_suffix(aux, multi_aux)
                        for coil in coils:
                            coil_part = "" if coil is None else f"-{coil}V"
                            sku = f"{base_sku}{coil_part}{aux_suffix}"
                            seen_skus.add(sku)
                            variant_slug = sku_to_slug(sku)
                            variant_defaults = {
                                "group": group,
                                "slug": variant_slug,
                                "execution": variant_execution,
                                "coil_type": coil_type,
                                "coil_voltage_v": coil,
                                "aux_contacts": aux,
                                "is_default": variant_index == 0,
                                "is_active": True,
                            }
                            if dry_run:
                                self.stdout.write(
                                    f"  variant {sku} ({variant_execution}, {coil}V, aux={aux or '—'})"
                                )
                            else:
                                _, v_created = ProductVariant.objects.update_or_create(
                                    sku_code=sku,
                                    defaults=variant_defaults,
                                )
                                if v_created:
                                    variants_created += 1
                                else:
                                    variants_updated += 1
                            variant_index += 1

        pruned_variants = pruned_groups = 0
        if options["prune"] and not dry_run:
            pruned_variants = (
                ProductVariant.objects.exclude(sku_code__in=seen_skus)
                .filter(group__product_type__in=("KT", "KTP", "KTE"))
                .update(is_active=False)
            )
            pruned_groups = (
                ProductGroup.objects.filter(product_type__in=("KT", "KTP", "KTE"))
                .exclude(slug__in=seen_group_slugs)
                .update(is_active=False)
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Text import from {path.name}: {len(pages)} pages, "
                f"{groups_created} new groups, {groups_updated} updated groups, "
                f"{variants_created} new variants, {variants_updated} updated variants"
                + (f", pruned {pruned_variants} variants, {pruned_groups} groups" if options["prune"] else "")
            )
        )

    def _parse_int_spec(self, value: str | None) -> int | None:
        if not value:
            return None
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
        coil_ac = specs.get("Номинальное напряжение втягивающей катушки переменного тока", "")
        coil_dc = specs.get("Номинальное напряжение втягивающей катушки постоянного тока", "")
        if coil_ac:
            ProductSpec.objects.update_or_create(
                group=group,
                spec_key="coil_voltage_ac",
                defaults={"spec_value": coil_ac, "spec_unit": "В", "filterable": True},
            )
        if coil_dc:
            ProductSpec.objects.update_or_create(
                group=group,
                spec_key="coil_voltage_dc",
                defaults={"spec_value": coil_dc, "spec_unit": "В", "filterable": True},
            )

        aux_raw = parse_aux_contacts_raw(specs)
        if aux_raw:
            ProductSpec.objects.update_or_create(
                group=group,
                spec_key="aux_contacts",
                defaults={"spec_value": aux_raw, "spec_unit": "", "filterable": False},
            )

        for label, (key, unit, filterable) in mapping.items():
            if label in specs:
                val = specs[label].replace("А", "").replace("В", "").replace("Гц", "").strip()
                ProductSpec.objects.update_or_create(
                    group=group,
                    spec_key=key,
                    defaults={
                        "spec_value": val.split()[0] if val else specs[label],
                        "spec_unit": unit,
                        "filterable": filterable,
                    },
                )
