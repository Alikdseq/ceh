from pathlib import Path

import pytest

from apps.products.services.other_catalog_docx import parse_other_catalog_docx, resolve_other_catalog_docx


@pytest.fixture
def other_catalog_docx_path():
    root = Path(__file__).resolve().parents[4]
    try:
        return resolve_other_catalog_docx(root / "КАТАЛОГ остальной продукции.docx")
    except FileNotFoundError:
        pytest.skip("КАТАЛОГ остальной продукции.docx not found")


def test_parse_other_catalog_docx_sections(other_catalog_docx_path):
    sections = parse_other_catalog_docx(other_catalog_docx_path)
    keys = {section.section_key for section in sections}
    assert "kte-01-25" in keys
    assert "kte-02-160" in keys
    assert "kte-02-250" in keys
    assert "pvp-17-29" in keys
    assert "pvp-17-31" in keys
    assert "vpk-3110" in keys


def test_parse_other_catalog_docx_kte_specs(other_catalog_docx_path):
    sections = parse_other_catalog_docx(other_catalog_docx_path)
    kte = next(section for section in sections if section.section_key == "kte-01-25")
    assert "25" in kte.specs.get("Номинальный ток главной цепи", "")
    assert "550" in kte.specs.get("Номинальное напряжение главной цепи контакта", "")
