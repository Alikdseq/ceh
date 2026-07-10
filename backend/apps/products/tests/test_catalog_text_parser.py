from pathlib import Path

import pytest

from apps.products.services.catalog_parser import (
    parse_catalog_text_file,
    parse_coil_voltages,
    parse_model_code,
)


@pytest.fixture
def catalog_text_path():
    root = Path(__file__).resolve().parents[4]
    for candidate in (root / "data" / "тексткаталога.txt", root / "тексткаталога.txt"):
        if candidate.exists():
            return candidate
    pytest.skip("тексткаталога.txt not found")


def test_parse_catalog_text_file_finds_pages(catalog_text_path):
    pages = parse_catalog_text_file(catalog_text_path)
    assert len(pages) >= 40
    first = pages[0]
    assert first.models
    assert "КТ6012" in first.models[0] or "КТ6012" in first.purpose
    assert first.specs.get("Номинальная сила тока")


def test_parse_catalog_text_includes_coil_voltages(catalog_text_path):
    pages = parse_catalog_text_file(catalog_text_path)
    kt_page = next(p for p in pages if any("КТ6012" in m for m in p.models))
    coil_spec = kt_page.specs.get(
        "Номинальное напряжение втягивающей катушки переменного тока", ""
    )
    assert "36" in coil_spec or "110" in coil_spec


def test_parse_coil_voltages_from_catalog_format():
    assert parse_coil_voltages("36В,110В,220В,380В") == [36, 110, 220, 380]


def test_parse_model_code_extracts_four_ac_coils():
    specs = {
        "Номинальная сила тока": "100 А",
        "Номинальное напряжение втягивающей катушки переменного тока": "36В,110В,220В,380В",
    }
    parsed = parse_model_code("КТ6012Б-У3", specs)
    assert parsed.coil_voltages_ac == [36, 110, 220, 380]
