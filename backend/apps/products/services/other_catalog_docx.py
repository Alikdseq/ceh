"""Parse «КАТАЛОГ остальной продукции.docx» into product sections."""

from __future__ import annotations

import re
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

from apps.products.services.catalog_parser import parse_specs_block

_W_NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


@dataclass
class OtherCatalogSection:
    section_key: str
    purpose: str = ""
    models_line: str = ""
    specs: dict[str, str] = field(default_factory=dict)
    meta: dict[str, str] = field(default_factory=dict)


def _read_docx_paragraphs(docx_path: Path) -> list[str]:
    with zipfile.ZipFile(docx_path) as archive:
        xml = archive.read("word/document.xml")
    root = ET.fromstring(xml)
    paragraphs: list[str] = []
    for paragraph in root.findall(".//w:p", _W_NS):
        texts = [node.text or "" for node in paragraph.findall(".//w:t", _W_NS)]
        line = "".join(texts).strip()
        if line:
            paragraphs.append(line)
    return paragraphs


def _section_key_from_text(text: str) -> str | None:
    upper = text.upper().replace(" ", "")
    if "КТЭ01-25" in upper or "01-25" in text:
        if "02" not in text[:20]:
            return "kte-01-25"
    if "02-250" in text or "02–250" in text:
        return "kte-02-250"
    if "02-160" in text or "02–160" in text:
        return "kte-02-160"
    if "17-29" in text or "17–29" in text or "ПВП1729" in upper:
        return "pvp-17-29"
    if "17-31" in text or "17–31" in text or "ПВП1731" in upper:
        return "pvp-17-31"
    if "ВПК3110" in upper or "ВПК 3110" in text:
        return "vpk-3110"
    return None


def _normalize_spec_lines(lines: list[str]) -> str:
    normalized: list[str] = []
    for line in lines:
        cleaned = line.strip()
        if not cleaned or cleaned == "АО «Электроконтактор»":
            continue
        cleaned = re.sub(r"\s+", " ", cleaned)
        if " – " not in cleaned and " - " not in cleaned:
            if re.match(r"^\d+\.\d+\.\d+", cleaned):
                normalized.append(f"ТУ – {cleaned}")
            elif cleaned.upper().startswith("ВЫКЛЮЧАТЕЛЬ ПУТЕВОЙ ТИПА"):
                normalized.append(f"Тип – {cleaned}")
            continue
        normalized.append(cleaned)
    return "\n".join(normalized)


def parse_other_catalog_docx(docx_path: Path) -> list[OtherCatalogSection]:
    paragraphs = _read_docx_paragraphs(docx_path)
    sections: list[OtherCatalogSection] = []
    current: OtherCatalogSection | None = None
    mode: str | None = None
    spec_lines: list[str] = []

    for line in paragraphs:
        if line.strip() == "Назначение":
            if current and current.section_key and current.purpose:
                block = _normalize_spec_lines(spec_lines)
                current.specs = parse_specs_block(block)
                if "Тип" in current.specs:
                    current.meta["type_designation"] = current.specs.pop("Тип")
                if "ТУ" in current.specs:
                    current.meta["tu"] = current.specs.pop("ТУ")
                sections.append(current)
            current = OtherCatalogSection(section_key="")
            mode = "purpose"
            spec_lines = []
            continue

        if current is None:
            continue

        if line.startswith("Основные технические характеристики"):
            mode = "specs"
            continue

        if line.startswith("ПАКЕТНЫЕ ПЕРЕКЛЮЧАТЕЛИ:"):
            current.models_line = line
            if not current.section_key:
                current.section_key = _section_key_from_text(line) or ""
            continue

        if mode == "purpose":
            if not current.section_key:
                key = _section_key_from_text(line)
                if key:
                    current.section_key = key
            if current.purpose:
                current.purpose += "\n"
            current.purpose += line
            continue

        if mode == "specs":
            spec_lines.append(line)

    if current and current.section_key and current.purpose:
        block = _normalize_spec_lines(spec_lines)
        current.specs = parse_specs_block(block)
        if "Тип" in current.specs:
            current.meta["type_designation"] = current.specs.pop("Тип")
        if "ТУ" in current.specs:
            current.meta["tu"] = current.specs.pop("ТУ")
        sections.append(current)

    deduped: dict[str, OtherCatalogSection] = {}
    for section in sections:
        if section.section_key:
            deduped[section.section_key] = section
    return list(deduped.values())


def resolve_other_catalog_docx(path: Path) -> Path:
    if path.exists():
        return path
    backend_root = Path(__file__).resolve().parents[3]
    repo_root = backend_root.parent
    for candidate in (
        path,
        repo_root / path.name,
        repo_root / "data" / path.name,
        Path("/data") / path.name,
    ):
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"Other products catalog docx not found: {path}")
