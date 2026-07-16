import pytest

from apps.products.services.catalog_query_parse import latinize_catalog_token, parse_product_query


@pytest.mark.parametrize(
    "raw,series,ptype,execution",
    [
        ("кт6023", "6023", "KT", None),
        ("КТ 6023", "6023", "KT", None),
        ("KT6023", "6023", "KT", None),
        ("kt6023b", "6023", "KT", "B"),
        ("ktp6023", "6023", "KTP", None),
        ("6023", "6023", None, None),
    ],
)
def test_parse_product_query_variants(raw, series, ptype, execution):
    parsed = parse_product_query(raw)
    assert parsed is not None
    assert parsed.series_code == series
    assert parsed.product_type == ptype
    assert parsed.execution == execution


def test_latinize_catalog_token():
    assert latinize_catalog_token("КТ 6023-БС") == "kt6023bs"
