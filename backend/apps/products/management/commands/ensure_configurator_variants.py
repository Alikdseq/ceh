"""
Ensure product cards have coil / aux-contact variants for the configurator chips.
Uses specs imported from catalog text (coil_voltage_ac/dc, aux_contacts).
"""
from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.products.models import ProductGroup, ProductSpec, ProductVariant
from apps.products.services.catalog_parser import (
    AUX_CONTACT_2Z2R,
    AUX_CONTACT_3Z3R,
    aux_contacts_sku_suffix,
    parse_aux_contacts_options,
    parse_aux_contacts_raw,
    parse_coil_voltages,
    sku_to_slug,
)
from apps.products.utils import invalidate_catalog_cache


def _coils_for_group(group: ProductGroup) -> list[int | None]:
    ac = ProductSpec.objects.filter(group=group, spec_key="coil_voltage_ac").first()
    dc = ProductSpec.objects.filter(group=group, spec_key="coil_voltage_dc").first()
    coils: list[int] = []
    if group.product_type == "KTP" and dc:
        coils = parse_coil_voltages(dc.spec_value)
    elif ac:
        coils = parse_coil_voltages(ac.spec_value)
    elif dc:
        coils = parse_coil_voltages(dc.spec_value)
    if not coils:
        return [None]
    return coils


def _aux_for_group(group: ProductGroup) -> list[str]:
    raw_spec = ProductSpec.objects.filter(group=group, spec_key="aux_contacts").first()
    specs_map = {"Количество вспомогательных контактов": raw_spec.spec_value} if raw_spec else {}
    options = parse_aux_contacts_options(specs_map)
    if options:
        return options
    raw = raw_spec.spec_value if raw_spec else parse_aux_contacts_raw(specs_map)
    if raw and ("2 замыкающих" in raw or "3 замыкающих" in raw):
        out: list[str] = []
        if "2 замыкающих" in raw:
            out.append(AUX_CONTACT_2Z2R)
        if "3 замыкающих" in raw:
            out.append(AUX_CONTACT_3Z3R)
        if out:
            return out
    return [""]


class Command(BaseCommand):
    help = "Create missing coil/aux variants for configurator chips on product cards"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")

    @transaction.atomic
    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        created = updated = skipped = 0

        qs = ProductGroup.objects.filter(is_active=True, product_type__in=("KT", "KTP")).prefetch_related(
            "variants", "specs",
        )

        for group in qs:
            active = [v for v in group.variants.all() if v.is_active]
            if not active:
                skipped += 1
                continue

            coils = _coils_for_group(group)
            aux_options = _aux_for_group(group)
            has_coil = any(v.coil_voltage_v is not None for v in active)
            aux_values = {v.aux_contacts for v in active if v.aux_contacts}
            needs_coil = any(c is not None for c in coils) and not has_coil
            needs_aux = len(aux_options) > 1 and len(aux_values) < 2
            if not needs_coil and not needs_aux:
                skipped += 1
                continue

            base = next((v for v in active if v.is_default), None) or next((v for v in active if v.price), None)
            if not base:
                skipped += 1
                continue

            multi_aux = len(aux_options) > 1
            base_sku = base.sku_code
            for suffix in ("-220V", "-380V", "-36V", "-127V", "-660V", "-2Z2R", "-3Z3R"):
                if base_sku.upper().endswith(suffix):
                    base_sku = base_sku[: -len(suffix)]
            if "-У" in base_sku.upper():
                idx = base_sku.upper().find("-У")
                base_sku = base_sku[:idx]

            coil_type = "DC" if group.product_type == "KTP" else "AC"
            index = 0
            for aux in aux_options:
                aux_suffix = aux_contacts_sku_suffix(aux, multi_aux)
                for coil in coils:
                    coil_part = "" if coil is None else f"-{coil}V"
                    sku = f"{base_sku}{coil_part}{aux_suffix}"
                    if ProductVariant.objects.filter(sku_code=sku).exists():
                        variant = ProductVariant.objects.get(sku_code=sku)
                        if variant.coil_voltage_v != coil or variant.aux_contacts != aux:
                            if not dry_run:
                                variant.coil_voltage_v = coil
                                variant.aux_contacts = aux
                                variant.save(update_fields=["coil_voltage_v", "aux_contacts"])
                            updated += 1
                        continue

                    if dry_run:
                        self.stdout.write(f"  + {group.slug}: {sku}")
                        created += 1
                        continue

                    ProductVariant.objects.create(
                        group=group,
                        sku_code=sku,
                        slug=sku_to_slug(sku),
                        execution=base.execution,
                        coil_type=coil_type,
                        coil_voltage_v=coil,
                        aux_contacts=aux,
                        price=base.price,
                        price_valid_from=base.price_valid_from,
                        is_active=True,
                        is_default=index == 0 and not active,
                    )
                    created += 1
                    index += 1

        if not dry_run:
            invalidate_catalog_cache()

        self.stdout.write(
            self.style.SUCCESS(
                f"Configurator variants: +{created} created, {updated} updated, {skipped} skipped"
            )
        )
