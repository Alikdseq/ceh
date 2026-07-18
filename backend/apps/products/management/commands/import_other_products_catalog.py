import re
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify

from apps.products.models import Category, ProductGroup, ProductSpec, ProductVariant
from apps.products.services.other_catalog_docx import (
    OtherCatalogSection,
    parse_other_catalog_docx,
    resolve_other_catalog_docx,
)

SPEC_KEY_MAP = {
    "Номинальное напряжение главной цепи контакта": "nominal_voltage",
    "Номинальный ток главной цепи": "nominal_current",
    "Номинальное напряжение цепи управления": "control_voltage",
    "Коммутационная износостойкость, тыс. циклов ВО": "commutation_endurance",
    "Механическая износостойкость, млн. циклов ВО": "mechanical_endurance",
    "Масса не более": "weight_max",
    "Количество вспомогательных контактов": "aux_contacts",
    "Провал контактов, мм": "contact_wear_mm",
    "Раствор контактов,мм": "contact_gap_mm",
    "Конечное нажатие на месте контроля,Н": "control_force_n",
    "Материал главных контактов": "main_contact_material",
    "Условный тепловой ток на открытом воздухе": "thermal_current",
    "Номинальное рабочее напряжение": "nominal_voltage",
    "Частота переменного тока": "frequency",
    "Номинальное напряжение изоляции": "insulation_voltage",
    "Число коммутационных цепей": "commutation_circuits",
    "Число пакетов": "packet_count",
    "I ном. , А": "nominal_current",
    "U ном. перем. , В": "nominal_voltage_ac",
    "U ном. пост. , В": "nominal_voltage_dc",
    "Рабочее усилие срабатывания Н, не более": "operating_force_n",
    "Степень защиты": "ip_rating",
    "Температура окружающей среды, °С": "ambient_temperature",
    "Масса, кг, не более": "weight_max",
    "Содержание серебра, г": "silver_content",
    "Габаритные размеры, мм": "overall_dimensions",
}


class Command(BaseCommand):
    help = "Import descriptions and specs for KTE, PVP and VPK from «КАТАЛОГ остальной продукции.docx»"

    def add_arguments(self, parser):
        parser.add_argument(
            "docx_path",
            nargs="?",
            default="КАТАЛОГ остальной продукции.docx",
            type=str,
            help="Path to other products catalog DOCX",
        )
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="Replace existing descriptions and specs",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report changes without writing to DB",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        try:
            path = resolve_other_catalog_docx(Path(options["docx_path"]))
        except FileNotFoundError as exc:
            raise CommandError(str(exc)) from exc

        sections = parse_other_catalog_docx(path)
        if not sections:
            raise CommandError(f"No sections parsed from {path}")

        dry_run = options["dry_run"]
        overwrite = options["overwrite"]
        updated_groups = 0
        updated_specs = 0

        for section in sections:
            groups = self._groups_for_section(section)
            if not groups:
                self.stdout.write(self.style.WARNING(f"No groups for {section.section_key}"))
                continue

            for group in groups:
                changed = self._apply_section(group, section, overwrite=overwrite, dry_run=dry_run)
                if changed:
                    updated_groups += 1
                updated_specs += self._apply_specs(group, section, overwrite=overwrite, dry_run=dry_run)

        if dry_run:
            transaction.set_rollback(True)

        self.stdout.write(self.style.SUCCESS(
            f"Other catalog: {len(sections)} sections, {updated_groups} groups updated, "
            f"{updated_specs} spec rows upserted"
        ))

    def _groups_for_section(self, section: OtherCatalogSection) -> list[ProductGroup]:
        if section.section_key == "vpk-3110":
            group = self._ensure_vpk_group()
            return [group] if group else []

        category = Category.objects.filter(slug=section.section_key).first()
        if not category:
            return []
        return list(ProductGroup.objects.filter(category=category, is_active=True))

    def _ensure_vpk_group(self) -> ProductGroup | None:
        category = Category.objects.filter(slug="vyklyuchateli-putevye").first()
        if not category:
            return None

        variant = ProductVariant.objects.filter(
            sku_code__icontains="ВПК3110",
            is_active=True,
        ).select_related("group").first()
        if not variant:
            variant = ProductVariant.objects.filter(
                sku_code__icontains="ВЫКЛЮЧАТЕЛЬПУТЕВОЙ",
                is_active=True,
            ).select_related("group").first()

        defaults = {
            "category": category,
            "name": "Выключатель путевой ВПК 3110",
            "product_type": "SWITCH",
            "is_active": True,
        }
        group, _ = ProductGroup.objects.get_or_create(slug="vpk-3110", defaults=defaults)
        changed = False
        for field, value in defaults.items():
            if getattr(group, field) != value:
                setattr(group, field, value)
                changed = True
        if changed:
            group.save()

        if variant and variant.group_id != group.id:
            variant.group = group
            variant.save(update_fields=["group"])

        return group

    def _apply_section(
        self,
        group: ProductGroup,
        section: OtherCatalogSection,
        *,
        overwrite: bool,
        dry_run: bool,
    ) -> bool:
        short = section.purpose.split("\n", 1)[0].strip()[:500]
        full = section.purpose.strip()
        if section.meta.get("type_designation"):
            full = f"{section.meta['type_designation']}\n\n{full}"
        if section.meta.get("tu"):
            full = f"{full}\n\nТУ {section.meta['tu']}"

        update_fields: list[str] = []
        if overwrite or not (group.short_description or "").strip():
            if group.short_description != short:
                group.short_description = short
                update_fields.append("short_description")
        if overwrite or not (group.full_description or "").strip():
            if group.full_description != full:
                group.full_description = full
                update_fields.append("full_description")

        current = self._parse_int(section.specs.get("Номинальный ток главной цепи"))
        if current is None:
            current = self._parse_int(section.specs.get("I ном. , А"))
        if current is None:
            current = self._parse_int(section.specs.get("Условный тепловой ток на открытом воздухе"))
        if current and group.nominal_current_a != current:
            group.nominal_current_a = current
            update_fields.append("nominal_current_a")

        voltage = self._parse_int(section.specs.get("Номинальное рабочее напряжение"))
        if voltage is None:
            voltage = self._parse_int(section.specs.get("Номинальное напряжение главной цепи контакта"))
        if voltage and group.nominal_voltage_v != voltage:
            group.nominal_voltage_v = voltage
            update_fields.append("nominal_voltage_v")

        if section.section_key.startswith("kte-") and group.product_type != "KTE":
            group.product_type = "KTE"
            update_fields.append("product_type")

        if not update_fields:
            return False
        if not dry_run:
            group.save(update_fields=update_fields)
        return True

    def _apply_specs(
        self,
        group: ProductGroup,
        section: OtherCatalogSection,
        *,
        overwrite: bool,
        dry_run: bool,
    ) -> int:
        count = 0
        for sort_order, (label, value) in enumerate(section.specs.items()):
            key = SPEC_KEY_MAP.get(label) or slugify(label, allow_unicode=False)[:100]
            if not key:
                continue
            existing = ProductSpec.objects.filter(group=group, spec_key=key).first()
            if existing and not overwrite and existing.spec_value:
                continue
            if not dry_run:
                ProductSpec.objects.update_or_create(
                    group=group,
                    spec_key=key,
                    defaults={
                        "spec_value": value,
                        "spec_unit": "",
                        "filterable": key in {"nominal_current", "nominal_voltage", "packet_count"},
                        "sort_order": sort_order,
                    },
                )
            count += 1
        return count

    def _parse_int(self, value: str | None) -> int | None:
        if not value:
            return None
        match = re.search(r"(\d+)", value.replace(",", "."))
        return int(match.group(1)) if match else None
