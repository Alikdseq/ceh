from apps.products.services.catalog_parser import build_pvp_display_name


class _Group:
    def __init__(self, *, product_type, slug, name="", nominal_current_a=None, sku_code=""):
        self.product_type = product_type
        self.slug = slug
        self.name = name
        self.nominal_current_a = nominal_current_a
        self.variants = _Variants(sku_code)


class _Variants:
    def __init__(self, sku_code: str):
        self._sku = sku_code

    def filter(self, **kwargs):
        return self

    def order_by(self, *args):
        return self

    def first(self):
        if not self._sku:
            return None
        return type("V", (), {"sku_code": self._sku, "is_default": True})()


def test_pvp_pack_names():
    g = _Group(
        product_type="SWITCH",
        slug="17-29632",
        name="ПВП172963А2ПАКЕТНЫЙ",
        sku_code="ПВП172963А2ПАКЕТНЫЙ",
    )
    assert build_pvp_display_name(g) == "ПВП1729"


def test_pvp_63a_names():
    g = _Group(
        product_type="SWITCH",
        slug="17-29-63-2",
        name="ПВП172963А",
        sku_code="ПВП172963А",
        nominal_current_a=63,
    )
    assert build_pvp_display_name(g) == "ПВП1729 63А"


def test_pvp_100a_names():
    g = _Group(
        product_type="SWITCH",
        slug="17-31-100-3",
        name="ПВП1731100А",
        sku_code="ПВП1731100А",
        nominal_current_a=100,
    )
    assert build_pvp_display_name(g) == "ПВП1731 100А"
