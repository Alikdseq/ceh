from apps.products.services.catalog_parser import (
    format_cam_display_name,
    format_kte_display_name,
    normalize_pricelist_name,
)


def test_format_kte_display_name_from_pricelist():
    assert format_kte_display_name("КТЭ 01-25 (без бвк)") == "КТЭ 01-25 БЕЗБВК"
    assert format_kte_display_name("КТЭ 02-160 (1 бвк)") == "КТЭ 02-160 1БВК"
    assert format_kte_display_name("КТЭ 01-25 БЕЗБВК") == "КТЭ 01-25 БЕЗБВК"


def test_format_cam_display_name():
    assert format_cam_display_name("КЭ-42") == "КЭ-42"
    assert format_cam_display_name("ЭУ-1") == "ЭУ-1"
    assert format_cam_display_name("Кулачковый элемент КЭ-46", "KE46") == "КЭ-46"


def test_normalize_pricelist_kte_and_cam_names():
    kte = normalize_pricelist_name("КТЭ 02-250 (2 бвк)")
    assert kte["name"] == "КТЭ 02-250 2БВК"
    assert kte["product_type"] == "KTE"

    cam = normalize_pricelist_name("КЭ-54")
    assert cam["name"] == "КЭ-54"
    assert cam["product_type"] == "CAM"
