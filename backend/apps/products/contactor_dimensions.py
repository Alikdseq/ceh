"""Габаритные размеры контакторов КТ/КТП (мм) — по чертежу серии 6013–6053."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ContactorDimensions:
    l1: int
    l2: int
    b: int
    h: int

    def as_spec_value(self) -> str:
        return f"L1 — {self.l1} мм, L2 — {self.l2} мм, B — {self.b} мм, H — {self.h} мм"


# Ключ: (product_type, series_code)
_DIMENSIONS: dict[tuple[str, str], ContactorDimensions] = {}

_SMALL = ContactorDimensions(380, 350, 209, 140)
_SMALL_6633 = ContactorDimensions(380, 350, 209, 160)
_MED = ContactorDimensions(480, 450, 280, 175)
_MED_TALL = ContactorDimensions(480, 450, 280, 220)
_LARGE_6052 = ContactorDimensions(580, 550, 300, 230)
_LARGE_6053 = ContactorDimensions(680, 650, 300, 230)
_KTP_6052_OVERRIDE = ContactorDimensions(680, 550, 300, 230)


def _register(product_type: str, series_codes: tuple[str, ...], dims: ContactorDimensions) -> None:
    for series in series_codes:
        _DIMENSIONS[(product_type, series)] = dims


for pt in ("KT", "KTP"):
    _register(pt, ("6012", "6013", "6022", "6023", "6014", "6024"), _SMALL)
    _register(pt, ("6032", "6033"), _MED)
    _register(pt, ("6042", "6043"), _MED_TALL)

_register("KT", ("6632", "6633", "6634", "6612", "6622", "6623"), _SMALL_6633)
_register("KTP", ("6633",), _SMALL_6633)
_register("KT", ("6642", "6643", "6652"), _MED_TALL)
_register("KTP", ("6642", "6643"), _MED_TALL)

_register("KT", ("6052", "6652"), _LARGE_6052)
_register("KT", ("6053", "6653"), _LARGE_6053)
_register("KTP", ("6052", "6652"), _KTP_6052_OVERRIDE)
_register("KTP", ("6053", "6653"), _LARGE_6053)


def dimensions_for(product_type: str, series_code: str) -> ContactorDimensions | None:
    if not series_code:
        return None
    series = series_code.replace(" ", "")[:4]
    return _DIMENSIONS.get((product_type.upper(), series))
