from apps.products.services.catalog_parser import (
    AUX_CONTACT_2Z2R,
    AUX_CONTACT_3Z3R,
    aux_contacts_sku_suffix,
    parse_aux_contacts_options,
)


def test_parse_aux_contacts_both_options():
    specs = {
        "Количество вспомогательных контактов": (
            "(2 замыкающих и 2 размыкающих) или (3 замыкающих и 3 размыкающих)"
        ),
    }
    assert parse_aux_contacts_options(specs) == [AUX_CONTACT_2Z2R, AUX_CONTACT_3Z3R]


def test_parse_aux_contacts_single_2z2r():
    specs = {"Количество вспомогательных контактов": "(2 замыкающих и 2 размыкающих)"}
    assert parse_aux_contacts_options(specs) == [AUX_CONTACT_2Z2R]


def test_parse_aux_contacts_single_3z3r():
    specs = {"Количество вспомогательных контактов": "(3 замыкающих и 3 размыкающих)"}
    assert parse_aux_contacts_options(specs) == [AUX_CONTACT_3Z3R]


def test_aux_contacts_sku_suffix_only_when_multi():
    assert aux_contacts_sku_suffix(AUX_CONTACT_2Z2R, False) == ""
    assert aux_contacts_sku_suffix(AUX_CONTACT_2Z2R, True) == "-2Z2R"
    assert aux_contacts_sku_suffix(AUX_CONTACT_3Z3R, True) == "-3Z3R"
