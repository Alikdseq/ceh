"""Parse user search tokens like «кт6023», «KT 6023», «ktp6023бс» into catalog fields."""

from __future__ import annotations

import re
from dataclasses import dataclass

from apps.products.models import ProductGroup


@dataclass(frozen=True)
class ParsedProductQuery:
    product_type: str | None  # KT, KTP, KTE
    series_code: str
    execution: str | None  # B, BS, S


def latinize_catalog_token(text: str) -> str:
    s = text.strip().lower().replace(" ", "").replace("-", "")
    for cyr, lat in (
        ("ктп", "ktp"),
        ("ктэ", "kte"),
        ("кт", "kt"),
        ("бс", "bs"),
    ):
        s = s.replace(cyr, lat)
    s = s.replace("б", "b").replace("с", "s")
    return s


def parse_product_query(raw: str) -> ParsedProductQuery | None:
    """
    Extract series (4 digits), optional type prefix, optional execution suffix.
    Returns None if the string does not look like a catalog model query.
    """
    if not raw or not raw.strip():
        return None

    token = latinize_catalog_token(raw)
    if len(token) < 4:
        return None

    product_type: str | None = None
    if token.startswith("ktp"):
        product_type = ProductGroup.ProductType.KTP
        token = token[3:]
    elif token.startswith("kte"):
        product_type = ProductGroup.ProductType.KTE
        token = token[3:]
    elif token.startswith("kt"):
        product_type = ProductGroup.ProductType.KT
        token = token[2:]

    execution: str | None = None
    for suffix, code in (("bs", "BS"), ("b", "B"), ("s", "S")):
        if token.endswith(suffix) and len(token) > len(suffix) + 3:
            execution = code
            token = token[: -len(suffix)]
            break

    m = re.fullmatch(r"(\d{4})", token)
    if not m:
        m = re.search(r"(\d{4})", token)
        if not m:
            return None
    series = m.group(1)

    return ParsedProductQuery(
        product_type=product_type,
        series_code=series,
        execution=execution,
    )
