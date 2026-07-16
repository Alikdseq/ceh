"""
Catalog import utilities — PDF parsing, SKU normalization, category mapping.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from django.utils.text import slugify

MODEL_RE = re.compile(
    r"КТ[П]?[\d]{4}[А-ЯA-Z0-9\-]*(?:У3|С-У3|-У3)?",
    re.IGNORECASE,
)
SPEC_LINE_RE = re.compile(r"^[\u2022\uF0B7•\-]\s*(.+?)\s*[–\-]\s*(.+)$", re.MULTILINE)
BULLET_ONLY_RE = re.compile(r"^[\u2022\uF0B7•\-–—\s]*$")
COIL_VOLTAGE_RE = re.compile(r"(\d+)\s*[ВVвv]", re.IGNORECASE)
COIL_AC_SPEC_KEY = "Номинальное напряжение втягивающей катушки переменного тока"
COIL_DC_SPEC_KEY = "Номинальное напряжение втягивающей катушки постоянного тока"
AUX_CONTACTS_SPEC_KEY = "Количество вспомогательных контактов"
DEFAULT_KT_AC_COILS = [36, 110, 220, 380]
AUX_CONTACT_2Z2R = "2З+2Р"
AUX_CONTACT_3Z3R = "3З+3Р"


@dataclass
class ParsedPage:
    models: list[str] = field(default_factory=list)
    purpose: str = ""
    specs: dict[str, str] = field(default_factory=dict)
    honest_sign: bool = False


@dataclass
class ParsedModel:
    raw: str
    product_type: str  # KT, KTP, KTE
    series_code: str
    execution: str  # B, BS, S, NONE
    suffix: str = "У3"
    nominal_current_a: int | None = None
    coil_voltages_ac: list[int] = field(default_factory=list)
    coil_voltages_dc: list[int] = field(default_factory=list)


def parse_pdf_pages(pdf_path: Path) -> list[ParsedPage]:
    from pypdf import PdfReader

    reader = PdfReader(str(pdf_path))
    pages: list[ParsedPage] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(parse_page_text(text))
    return pages


def parse_catalog_extract(extract_path: Path) -> list[ParsedPage]:
    """Parse pre-extracted catalog text (=== PAGE N === blocks)."""
    text = extract_path.read_text(encoding="utf-8")
    pages: list[ParsedPage] = []
    blocks = re.split(r"=== PAGE \d+ ===", text)
    for block in blocks:
        block = block.strip()
        if block:
            pages.append(parse_page_text(block))
    return pages


def parse_catalog_text_file(text_path: Path) -> list[ParsedPage]:
    """Parse plain-text catalog export (blocks starting with «Назначение»)."""
    text = text_path.read_text(encoding="utf-8")
    blocks = re.split(r"(?=^Назначение\s*$)", text, flags=re.MULTILINE)
    pages: list[ParsedPage] = []
    for block in blocks:
        block = block.strip()
        if block.startswith("Назначение"):
            page = parse_page_text(block)
            if page.models or page.purpose:
                pages.append(page)
    return pages


def resolve_catalog_pages(path: Path) -> list[ParsedPage]:
    """Load pages from PDF or fallback to catalog_extract.txt."""
    if path.suffix.lower() == ".pdf" and path.exists():
        return parse_pdf_pages(path)
    if path.exists() and path.suffix.lower() == ".txt":
        if "назначение" in path.read_text(encoding="utf-8")[:500].lower():
            return parse_catalog_text_file(path)
        return parse_catalog_extract(path)

    extract = path.parent / "catalog_extract.txt"
    if extract.exists():
        return parse_catalog_extract(extract)

    parent = path.parent if path.parent.exists() else Path(".")
    for candidate in parent.glob("catalog_extract.txt"):
        return parse_catalog_extract(candidate)
    for candidate in parent.glob("*.pdf"):
        return parse_pdf_pages(candidate)

    raise FileNotFoundError(f"Catalog source not found: {path}")


def parse_page_text(text: str) -> ParsedPage:
    result = ParsedPage()
    result.honest_sign = "Честный знак" in text

    purpose_match = re.search(
        r"Назначение\s*\n(.+?)(?:\nОсновные|\n===|\Z)",
        text,
        re.DOTALL,
    )
    if purpose_match:
        purpose_block = purpose_match.group(1).strip()
        result.purpose = purpose_block
        result.models = list(dict.fromkeys(MODEL_RE.findall(purpose_block)))

    specs_match = re.search(
        r"Основные технические характеристики\s*\n(.+?)(?:\n\s*«|$)",
        text,
        re.DOTALL,
    )
    if specs_match:
        result.specs = parse_specs_block(specs_match.group(1))

    if not result.models:
        result.models = list(dict.fromkeys(MODEL_RE.findall(text)))

    return result


def parse_aux_contacts_raw(specs: dict[str, str]) -> str:
    """Return raw aux-contacts spec line from parsed specs."""
    if AUX_CONTACTS_SPEC_KEY in specs:
        return specs[AUX_CONTACTS_SPEC_KEY]
    for value in specs.values():
        if "вспомогательных контактов" in value.lower():
            return value
    return ""


def parse_aux_contacts_options(specs: dict[str, str]) -> list[str]:
    """
    Parse auxiliary contact options from catalog specs.
    Returns [] when not applicable, one label when fixed, two when «или» variants exist.
    """
    raw = parse_aux_contacts_raw(specs)
    if not raw:
        return []

    has_2 = "2 замыкающих и 2 размыкающих" in raw
    has_3 = "3 замыкающих и 3 размыкающих" in raw
    if not has_2 and not has_3:
        return []

    options: list[str] = []
    if has_2:
        options.append(AUX_CONTACT_2Z2R)
    if has_3:
        options.append(AUX_CONTACT_3Z3R)
    return options


def aux_contacts_sku_suffix(aux: str, multi: bool) -> str:
    """Append SKU suffix only when a group has multiple aux-contact variants."""
    if not aux or not multi:
        return ""
    compact = aux.replace("+", "").replace("З", "Z").replace("Р", "R")
    return f"-{compact}"


def parse_coil_voltages(spec: str) -> list[int]:
    """Extract unique coil voltages from strings like «36В,110В,220В,380В»."""
    seen: list[int] = []
    for match in COIL_VOLTAGE_RE.findall(spec or ""):
        value = int(match)
        if value not in seen:
            seen.append(value)
    return seen


def parse_specs_block(block: str) -> dict[str, str]:
    specs: dict[str, str] = {}
    for raw_line in block.split("\n"):
        line = raw_line.strip()
        if not line or BULLET_ONLY_RE.match(line) or "Электроконтактор" in line:
            continue
        line = line.lstrip("\u2022\uF0B7•- ").strip()
        if not line:
            continue
        if " – " in line:
            key, val = line.split(" – ", 1)
        elif " - " in line:
            key, val = line.split(" - ", 1)
        else:
            continue
        specs[key.strip()] = val.strip()
    return specs


def parse_model_code(raw: str, specs: dict | None = None) -> ParsedModel:
    specs = specs or {}
    raw = raw.replace(" ", "").upper()
    product_type = "KTP" if raw.startswith("КТП") else "KT"
    if raw.startswith("КТЭ"):
        product_type = "KTE"

    series_match = re.search(r"(\d{4})", raw)
    series_code = series_match.group(1) if series_match else ""

    execution = "NONE"
    if "БС" in raw or "BS" in raw:
        execution = "BS"
    elif re.search(r"Б(?![СС])", raw) or "B" in raw[4:8]:
        if "БС" not in raw:
            execution = "B"
    if "С-У3" in raw or raw.endswith("С") or "662" in series_code or "663" in series_code:
        if "Б" not in raw and "БС" not in raw:
            if series_code.startswith("66") or "С" in raw:
                execution = "S"

    current = None
    current_spec = specs.get("Номинальная сила тока", "")
    if current_spec:
        m = re.search(r"(\d+)", current_spec)
        if m:
            current = int(m.group(1))

    coil_ac: list[int] = []
    coil_dc: list[int] = []
    coil_spec = specs.get(COIL_AC_SPEC_KEY, "")
    if not coil_spec:
        coil_spec = specs.get(COIL_DC_SPEC_KEY, "")
    coil_ac = parse_coil_voltages(coil_spec)
    if not coil_ac and COIL_AC_SPEC_KEY in specs and product_type == "KT":
        coil_ac = list(DEFAULT_KT_AC_COILS)

    dc_spec = specs.get(COIL_DC_SPEC_KEY, "")
    coil_dc = parse_coil_voltages(dc_spec)

    return ParsedModel(
        raw=raw,
        product_type=product_type,
        series_code=series_code,
        execution=execution,
        nominal_current_a=current,
        coil_voltages_ac=coil_ac,
        coil_voltages_dc=coil_dc,
    )


def group_key_from_page(page: ParsedPage) -> tuple[str, int | None, str]:
    """Return (series_code, current, product_type) for ProductGroup."""
    if not page.models:
        return ("", None, "KT")
    parsed = parse_model_code(page.models[0], page.specs)
    return (parsed.series_code, parsed.nominal_current_a, parsed.product_type)


def build_group_name(
    product_type: str,
    series: str,
    current: int | None,
    execution: str | None = None,
) -> str:
    """Каталожное обозначение слитно, например КТ6012Б-У3."""
    prefix = {"KT": "КТ", "KTP": "КТП", "KTE": "КТЭ"}.get(product_type, "")
    if product_type in ("KT", "KTP") and series and execution not in (None, "", "NONE"):
        exec_char = {"B": "Б", "BS": "БС", "S": "С"}.get(execution, "")
        return f"{prefix}{series}{exec_char}"
    if product_type == "KTE" and series:
        if "-" in series:
            return f"КТЭ{series}-У3"
        if len(series) >= 4:
            return f"КТЭ{series[:2]}-{series[2:]}-У3"
        return f"КТЭ{series}-У3"
    return ""


def strip_climate_suffix(label: str) -> str:
    """Remove trailing -У3 / -У4 climate suffix from catalog designation."""
    return re.sub(r"-У\d+$", "", label.strip(), flags=re.IGNORECASE)


def build_catalog_display_name(group) -> str:
    """Имя карточки — каталожное обозначение без суффикса климатического исполнения."""
    variant = (
        group.variants.filter(is_active=True)
        .order_by("-is_default", "price", "sku_code")
        .first()
    )
    if variant and variant.sku_code:
        sku = variant.sku_code.replace(" ", "")
        match = re.match(r"^(.+?-У\d)", sku, re.IGNORECASE)
        if match:
            label = match.group(1)
            label = label.replace("у", "У").replace("-у", "-У")
            return strip_climate_suffix(label)
        head = re.match(r"^([A-ZА-Я0-9]+(?:-[A-ZА-Я0-9]+)?)", sku)
        if head:
            return strip_climate_suffix(head.group(1))

    if group.product_type in ("KT", "KTP", "KTE") and group.series_code:
        execution = (
            group.variants.filter(is_active=True)
            .exclude(execution="NONE")
            .values_list("execution", flat=True)
            .first()
        )
        catalog = build_group_name(
            group.product_type,
            group.series_code,
            group.nominal_current_a,
            execution,
        )
        if catalog:
            return catalog

    raw = (group.name or "").strip()

    if group.product_type in ("CAM", "SWITCH", "ACCESSORY", "OTHER"):
        if variant and variant.sku_code:
            return re.sub(r"\s+", "", variant.sku_code)
        compact = re.sub(r"\s+", "", raw)
        if compact:
            return compact

    if raw and not raw.lower().startswith("контактор"):
        return re.sub(r"\s+", "", raw)
    return raw


def execution_slug_suffix(execution: str) -> str:
    return {"B": "b", "BS": "bs", "S": "s"}.get(execution, slugify(execution, allow_unicode=False))


def build_group_slug(
    product_type: str,
    series: str,
    current: int | None,
    execution: str | None = None,
) -> str:
    base = f"kontaktor-{product_type.lower()}-{series}"
    if current:
        base += f"-{current}a"
    if execution and execution not in ("NONE", ""):
        base += f"-{execution_slug_suffix(execution)}"
    return slugify(base, allow_unicode=False)


def category_slug_for_group(product_type: str, series: str, execution: str) -> str:
    if product_type == "KTP":
        if series.startswith("66"):
            return "ktp-6600"
        return "ktp-6000b"
    if product_type == "KTE":
        return "kontaktory-kte"
    if series.startswith("722"):
        return "kt-7200u"
    if execution == "S" or series.startswith("66"):
        return "kt-6600s"
    return "kt-6000b"


def sku_to_slug(sku: str) -> str:
    """Romanize SKU for unique URL slug (Б vs БС)."""
    s = sku.replace(" ", "").upper()
    replacements = [
        ("КТП", "ktp"), ("КТЭ", "kte"), ("КТ", "kt"),
        ("БС", "bs"), ("Б", "b"), ("У3", "u3"), ("С", "s"),
    ]
    for src, dst in replacements:
        s = s.replace(src, dst)
    slug = slugify(s.lower(), allow_unicode=False)
    return slug[:150] if slug else slugify(sku, allow_unicode=True)[:150]


def normalize_pricelist_name(name: str) -> dict:
    """Parse pricelist row name into structured data."""
    name = name.strip()
    upper = name.upper().replace(" ", "")

    product_type = "KT"
    if upper.startswith("КТП") or upper.startswith("KTP"):
        product_type = "KTP"
    elif upper.startswith("КТЭ") or upper.startswith("KTE"):
        product_type = "KTE"
    elif upper.startswith("ПВП") or "ПВП" in name:
        product_type = "SWITCH"
    elif upper.startswith("КЭ") or upper.startswith("ЭУ"):
        product_type = "CAM"
    elif upper.startswith("ВПК") or "МЕХ." in upper or "БЛОКИР" in upper or "БЛОК " in upper:
        product_type = "ACCESSORY"

    execution = "NONE"
    if "БС" in upper:
        execution = "BS"
    elif "Б" in upper and product_type in ("KT", "KTP"):
        execution = "B"
    elif "С" in upper and product_type == "KT":
        execution = "S"

    series = ""
    m = re.search(r"(\d{4})", upper)
    if m:
        series = m.group(1)
    elif product_type == "KTE":
        m2 = re.search(r"(\d{2}-\d+)", name)
        if m2:
            series = m2.group(1).replace("-", "")

    current = None
    m = re.search(r"(\d+)\s*А", name, re.IGNORECASE)
    if m:
        current = int(m.group(1))

    sku_base = re.sub(r"[^A-ZА-Я0-9]", "", upper)
    if product_type in ("KT", "KTP") and series and execution != "NONE":
        exec_char = {"B": "Б", "BS": "БС", "S": "С"}.get(execution, "")
        prefix = "КТП" if product_type == "KTP" else "КТ"
        sku_code = f"{prefix}{series}{exec_char}-У3"
    else:
        sku_code = sku_base[:50] if sku_base else slugify(name, allow_unicode=False)[:50].upper()

    display_name = name.strip()
    if product_type not in ("KT", "KTP", "KTE"):
        display_name = re.sub(r"\s+", "", display_name)

    return {
        "name": display_name,
        "product_type": product_type,
        "series_code": series,
        "execution": execution,
        "nominal_current_a": current,
        "sku_code": sku_code,
        "slug": sku_to_slug(sku_code),
    }


def pricelist_category_slug(row: dict, notes: str = "") -> str:
    pt = row["product_type"]
    series = row.get("series_code", "")
    if pt == "KT":
        return category_slug_for_group("KT", series, row.get("execution", "NONE"))
    if pt == "KTP":
        return category_slug_for_group("KTP", series, row.get("execution", "NONE"))
    if pt == "KTE":
        if "01" in row["name"]:
            return "kte-01-25"
        if "160" in row["name"]:
            return "kte-02-160"
        return "kte-02-250"
    if pt == "ACCESSORY":
        if "БЛОКИР" in row["name"].upper() or "МЕХ" in row["name"].upper():
            return "meh-blokirovki"
        return "katushki-upravleniya"
    if pt == "SWITCH":
        if "ПВП 17-29" in row["name"]:
            return "pvp-17-29"
        if "ПВП 17-31" in row["name"]:
            return "pvp-17-31"
        return "vyklyuchateli-putevye"
    if pt == "CAM":
        if row["name"].upper().startswith("ЭУ"):
            return "eu-serii"
        return "ke-serii"
    return "kontaktory-kt"
