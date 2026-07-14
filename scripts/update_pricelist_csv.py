#!/usr/bin/env python3
"""Update data/pricelist.csv: +22% VAT, PVP manual prices, КТ6032БС row."""
import csv
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "pricelist.csv"
VAT = Decimal("1.22")

PVP = {
    "ПВП 17-29 (63А) 2-пакетный": 3240,
    "ПВП 17-29 (63А) 3-пакетный": 3950,
    "ПВП 17-29 (63А) 5-пакетный": 6400,
    "ПВП 17-31 (100А) 2-пакетный": 3660,
    "ПВП 17-31 (100А) 3-пакетный": 4370,
    "ПВП 17-31 (100А) 5-пакетный": 8650,
}

KT6032BS = {
    "category": "Контакторы",
    "sku_name": "КТ 6032БС (250А)",
    "price_rub": "21425",
    "nominal_current_a": "250",
    "product_type": "KT",
    "notes": "исполнение БС",
}


def main() -> None:
    rows = list(csv.DictReader(CSV_PATH.open(encoding="utf-8")))
    fieldnames = rows[0].keys()
    out: list[dict] = []
    for row in rows:
        name = row["sku_name"]
        if name in PVP:
            row["price_rub"] = str(PVP[name])
        else:
            net = Decimal(row["price_rub"].replace(" ", ""))
            row["price_rub"] = str(int((net * VAT).quantize(Decimal("1"), rounding=ROUND_HALF_UP)))
        out.append(row)
        if name == "КТ 6024БС (125А)":
            out.append(dict(KT6032BS))

    with CSV_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out)
    print(f"Updated {CSV_PATH} ({len(out)} rows)")


if __name__ == "__main__":
    main()
