"""Человекочитаемые подписи для админки каталога."""

from django.utils.text import slugify

# slug в БД → подпись в форме
SPEC_KEY_CHOICES: list[tuple[str, str]] = [
    ("nominal_current", "Номинальный ток"),
    ("nominal_voltage", "Номинальное напряжение"),
    ("frequency", "Номинальная частота"),
    ("poles", "Число полюсов"),
    ("application_category", "Категория применения"),
    ("coil_voltage_ac", "Напряжение катушки (переменный ток)"),
    ("coil_voltage_dc", "Напряжение катушки (постоянный ток)"),
    ("aux_contacts", "Вспомогательные контакты"),
    ("weight_net", "Масса нетто"),
    ("weight_gross", "Масса брутто"),
]

SPEC_KEY_LABELS: dict[str, str] = dict(SPEC_KEY_CHOICES)

AUX_CONTACTS_HELP = "Например: 2З+2Р или 3З+3Р — как на сайте в плашках выбора."
SKU_HELP = "Код из прайс-листа, например КТ6012Б-У3-220V"
SLUG_HELP = "Заполняется автоматически из артикула. Менять только при необходимости."


def spec_label(spec_key: str) -> str:
    return SPEC_KEY_LABELS.get(spec_key, spec_key.replace("_", " ").capitalize())


def auto_variant_slug(sku_code: str) -> str:
    from apps.products.services.catalog_parser import sku_to_slug

    base = sku_to_slug(sku_code)
    return base or slugify(sku_code, allow_unicode=False)[:150]
