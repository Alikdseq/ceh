"""Match product groups to the catalog photo rotation list (mirrors frontend product-images.ts)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

from apps.products.models import ProductGroup

ProductExecution = Literal["B", "BS", "S", "NONE"]

LISTED_IMAGE_ROTATION_DEGREES = 270

_ROTATED_PRODUCTS: list[tuple[str, str, ProductExecution, bool]] = [
    ("KT", "6014", "B", False),
    ("KT", "6014", "BS", False),
    ("KT", "6032", "B", False),
    ("KT", "6032", "BS", False),
    ("KT", "6043", "B", False),
    ("KT", "6043", "BS", False),
    ("KT", "6623", "S", False),
    ("KT", "6633", "NONE", False),
    ("KT", "6642", "S", False),
    ("KT", "7223", "NONE", True),
    ("KTP", "6012", "B", False),
    ("KTP", "6012", "BS", False),
    ("KTP", "6013", "B", False),
    ("KTP", "6013", "BS", False),
    ("KTP", "6032", "B", False),
    ("KTP", "6032", "BS", False),
    ("KTP", "6043", "B", False),
    ("KTP", "6043", "BS", False),
    ("KTP", "6633", "NONE", False),
    ("KTP", "6633", "B", False),
    ("KTP", "6633", "S", False),
]


@dataclass(frozen=True)
class ProductIdentity:
    product_type: Literal["KT", "KTP"]
    series: str
    execution: ProductExecution
    coil36v: bool


def _normalize_label(label: str) -> str:
    return re.sub(r"\s+", "", label).upper()


def _execution_from_tail(tail: str) -> ProductExecution:
    match = re.match(r"^(БС|БК|Б|С)", tail)
    if not match:
        return "NONE"
    token = match.group(1)
    if token == "БС":
        return "BS"
    if token == "БК":
        return "NONE"
    if token == "Б":
        return "B"
    return "S"


def _coil36v_from_labels(labels: list[str], coil_voltage_v: int | None) -> bool:
    if coil_voltage_v == 36:
        return True
    return any(re.search(r"36\s*V", _normalize_label(label), re.I) for label in labels)


def _should_rotate_by_catalog_name(labels: list[str], coil36v: bool) -> bool:
    for label in labels:
        compact = _normalize_label(label)
        if re.search(r"КТ6633", compact) and not re.search(r"6633(?:БС|Б|С)", compact):
            return True
        if re.search(r"КТ7223", compact) and coil36v:
            return True
    return False


def _resolve_identity(
    *,
    name: str = "",
    slug: str = "",
    sku_code: str = "",
    series_code: str = "",
    product_type: str = "",
    execution: str = "",
    coil_voltage_v: int | None = None,
) -> ProductIdentity | None:
    labels = [x for x in (name, sku_code, slug) if x]
    coil36v = _coil36v_from_labels(labels, coil_voltage_v)

    for label in labels:
        compact = _normalize_label(label)
        ktp = re.search(r"КТП(\d{4})", compact)
        if ktp:
            tail = compact[ktp.start() + len(ktp.group(0)) :]
            ex = _execution_from_tail(tail)
            if ex == "NONE" and execution:
                ex = execution if execution in ("B", "BS", "S", "NONE") else "NONE"
            return ProductIdentity("KTP", ktp.group(1), ex, coil36v)
        kt = re.search(r"КТ(\d{4})", compact)
        if kt:
            tail = compact[kt.start() + len(kt.group(0)) :]
            ex = _execution_from_tail(tail)
            if ex == "NONE" and execution:
                ex = execution if execution in ("B", "BS", "S", "NONE") else "NONE"
            return ProductIdentity("KT", kt.group(1), ex, coil36v)

    series = re.sub(r"\D", "", series_code or "")[:4]
    ptype = (product_type or "").upper()
    if not series or ptype not in ("KT", "KTP"):
        return None
    ex = execution if execution in ("B", "BS", "S", "NONE") else "NONE"
    return ProductIdentity(ptype, series, ex, coil36v)  # type: ignore[arg-type]


def _identities_match(left: ProductIdentity, right: ProductIdentity) -> bool:
    if left.product_type != right.product_type or left.series != right.series:
        return False
    if left.coil36v or right.coil36v:
        return left.coil36v == right.coil36v
    return left.execution == right.execution


def should_rotate_product_group(group: ProductGroup) -> bool:
    default = (
        group.variants.filter(is_active=True)
        .order_by("-is_default", "id")
        .first()
    )
    execution = default.execution if default else "NONE"
    coil_v = default.coil_voltage_v if default else None
    labels = [group.name, group.slug]
    if default:
        labels.append(default.sku_code)

    coil36v = _coil36v_from_labels(labels, coil_v)
    if _should_rotate_by_catalog_name(labels, coil36v):
        return True

    identity = _resolve_identity(
        name=group.name,
        slug=group.slug,
        sku_code=default.sku_code if default else "",
        series_code=group.series_code,
        product_type=group.product_type,
        execution=execution,
        coil_voltage_v=coil_v,
    )
    if not identity:
        return False

    for ptype, series, execution_rule, coil36v_rule in _ROTATED_PRODUCTS:
        rule = ProductIdentity(ptype, series, execution_rule, coil36v_rule)  # type: ignore[arg-type]
        if _identities_match(rule, identity):
            return True
    return False
