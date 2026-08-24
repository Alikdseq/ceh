"""Static catalog photo resolution — mirrors frontend/src/lib/product-images.ts."""

from __future__ import annotations

import re
from urllib.parse import quote

from apps.products.models import ProductGroup

_TOVAR_FILES = (
    "Кт6012.JPG",
    "КТ6013.JPG",
    "КТ6014.JPG",
    "КТ6022.JPG",
    "КТ6023.JPG",
    "Кт6024.JPG",
    "Кт6032.JPG",
    "Кт6032(2).JPG",
    "КТ6033.JPG",
    "КТ6033(2).JPG",
    "КТ6042.JPG",
    "КТ6043.JPG",
    "КТ6053.JPG",
    "КТ6613.JPG",
    "КТ6623.JPG",
    "КТ6632.JPG",
    "КТ6632(2).JPG",
    "КТ6633.JPG",
    "КТ6633(2).JPG",
    "Кт6642.JPG",
    "Кт6643.JPG",
    "КТ6653.JPG",
    "КТ7223.JPG",
    "КТ7223(2).JPG",
    "КТП6012.JPG",
    "КТП6013.JPG",
    "КТП6014.JPG",
    "КТП6022.JPG",
    "КТП6022(2).JPG",
    "КТП6024.JPG",
    "КТП6032.JPG",
    "КТП6032(2).JPG",
    "КТП6033.JPG",
    "КТП6033(2).JPG",
    "КТП6042.JPG",
    "КТП6042(2).JPG",
    "КТП6043.JPG",
    "КТП6043(2).JPG",
    "КТП6633.JPG",
    "КТП6633(2).JPG",
    "КТ6052Б.png",
    "КТ6612С.png",
    "КТ6622С.png",
    "КТ6634.png",
    "КТ6652С.png",
    "КТП6023Б.png",
    "КТП6053Б.png",
    "КТП6053БС.png",
    "КТП6613С.png",
    "КТП6622С.png",
    "КТП6623С.png",
    "КТП6632.png",
    "КТП6634.png",
    "КТП6652С.png",
)

_NAMED_IMAGES: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"пвп\s*17[-\s]*31|pvp\s*1731|17-31\s*\(100", re.I), "/tovar/ПВП1731.png"),
    (re.compile(r"пвп\s*17[-\s]*29|pvp\s*1729|17-29\s*\(63", re.I), "/tovar/ПВП17.png"),
    (re.compile(r"ктэ\s*01[-\s]*25|kte\s*0125|01-25", re.I), "/tovar/КТЭ0125.png"),
    (re.compile(r"ктэ\s*02[-\s]*160|kte\s*02160|02-160", re.I), "/tovar/КТЭ02250.png"),
    (re.compile(r"ктэ\s*02[-\s]*250|kte\s*02250|02-250", re.I), "/tovar/КТЭ02250.png"),
    (re.compile(r"блок\s*контакт", re.I), "/tovar/блокконтактов.jpeg"),
    (re.compile(r"выключатель\s*путев|впк\s*3110", re.I), "/tovar/Выклю Путевой 1.jpeg"),
    (re.compile(r"эу[\s-]*5", re.I), "/tovar/ЭУ5.jpg"),
    (re.compile(r"эу[\s-]*1\b", re.I), "/tovar/ЭУ1.jpg"),
    (re.compile(r"кэ[\s-]*46", re.I), "/tovar/КЭ-46.jpg"),
    (re.compile(r"кэ[\s-]*47", re.I), "/tovar/КЭ-47.jpg"),
    (re.compile(r"кэ[\s-]*54", re.I), "/tovar/КЭ-54.png"),
    (re.compile(r"кэ[\s-]*61", re.I), "/photos/кэ61.png"),
    (re.compile(r"ктп\s*6052|ktp6052", re.I), "/tovar/catalog-docx/image26.jpeg"),
    (re.compile(r"ктп\s*6643|ktp6643", re.I), "/tovar/catalog-docx/image24.jpeg"),
    (re.compile(r"ктп\s*6642|ktp6642", re.I), "/tovar/catalog-docx/image23.jpeg"),
    (re.compile(r"ктп\s*6653|ktp6653", re.I), "/tovar/catalog-docx/image25.jpeg"),
)

_CATALOG_DOCX_FALLBACK: dict[str, str] = {
    "KTP6052": "/tovar/catalog-docx/image26.jpeg",
    "KTP6653": "/tovar/catalog-docx/image25.jpeg",
    "KTP6643": "/tovar/catalog-docx/image24.jpeg",
    "KTP6642": "/tovar/catalog-docx/image23.jpeg",
    "KTP6623": "/tovar/КТП6623С.png",
}


def _tovar_public_url(filename: str) -> str:
    return f"/tovar/{quote(filename)}"


def _file_to_image_key(filename: str) -> str | None:
    base = re.sub(r"\.(jpe?g|png)$", "", filename, flags=re.I)
    base = re.sub(r"\(2\)$", "", base, flags=re.I)
    upper = base.upper()
    ktp = re.match(r"^КТП(\d{4})", upper)
    if ktp:
        return f"KTP{ktp.group(1)}"
    kt = re.match(r"^КТ(\d{4})", upper)
    if kt:
        return f"KT{kt.group(1)}"
    return None


def _build_image_map() -> dict[str, list[str]]:
    image_map: dict[str, list[str]] = {}
    for filename in _TOVAR_FILES:
        key = _file_to_image_key(filename)
        if not key:
            continue
        image_map.setdefault(key, []).append(_tovar_public_url(filename))
    for key, urls in image_map.items():
        urls.sort(key=lambda url: 1 if "%282%29" in url or "(2)" in url else 0)
    return image_map


_IMAGE_MAP = _build_image_map()


def _product_label(*, name: str = "", slug: str = "", series_code: str = "") -> str:
    return " ".join(part for part in (name, series_code, slug) if part)


def _resolve_named_image(label: str) -> str | None:
    if not label:
        return None
    for pattern, url in _NAMED_IMAGES:
        if pattern.search(label):
            return url
    return None


def _extract_series_code(*, name: str = "", slug: str = "", series_code: str = "") -> str | None:
    from_field = re.sub(r"\D", "", series_code or "")
    if len(from_field) >= 4:
        return from_field[:4]
    for source in (name, slug):
        if not source:
            continue
        ktp = re.search(r"КТП[\s-]*(\d{4})", source, re.I)
        if ktp:
            return ktp.group(1)
        kt = re.search(r"КТ[\s-]*(\d{4})", source, re.I)
        if kt:
            return kt.group(1)
        digits = re.search(r"(\d{4})", source)
        if digits:
            return digits.group(1)
    return None


def _resolve_image_key(*, name: str = "", slug: str = "", series_code: str = "", product_type: str = "") -> str | None:
    series = _extract_series_code(name=name, slug=slug, series_code=series_code)
    if not series:
        return None
    ptype = (product_type or "").upper()
    if ptype == "KTP":
        return f"KTP{series}"
    if ptype == "KT":
        return f"KT{series}"
    label = name or slug or ""
    if re.search(r"КТП", label, re.I):
        return f"KTP{series}"
    if re.search(r"КТ", label, re.I):
        return f"KT{series}"
    return None


def resolve_static_product_image_for_group(group: ProductGroup) -> str | None:
    """Return /tovar/ or /photos/ path used on the public site when CMS photo is absent."""
    label = _product_label(name=group.name or "", slug=group.slug or "", series_code=group.series_code or "")
    named = _resolve_named_image(label)
    if named:
        return named

    key = _resolve_image_key(
        name=group.name or "",
        slug=group.slug or "",
        series_code=group.series_code or "",
        product_type=group.product_type or "",
    )
    if not key:
        return None
    mapped = _IMAGE_MAP.get(key)
    if mapped:
        return mapped[0]
    return _CATALOG_DOCX_FALLBACK.get(key)


def static_url_basename(static_url: str) -> str | None:
    """Basename for seeding ProductImage.image when photo lives under /tovar/."""
    if static_url.startswith("/tovar/"):
        from urllib.parse import unquote

        return unquote(static_url.split("/tovar/", 1)[1])
    return None
