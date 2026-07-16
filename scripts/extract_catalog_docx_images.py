"""Extract embedded images from data/КАТАЛОГ.docx into frontend/public/tovar/catalog-docx/."""
from __future__ import annotations

import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DOCX_CANDIDATES = [
    REPO / "data" / "КАТАЛОГ.docx",
    REPO / "КАТАЛОГ (1).docx",
]
OUT_DIR = REPO / "frontend" / "public" / "tovar" / "catalog-docx"


def main() -> None:
    docx = next((p for p in DOCX_CANDIDATES if p.is_file()), None)
    if not docx:
        raise SystemExit("Catalog docx not found")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    count = 0
    with zipfile.ZipFile(docx) as archive:
        for name in archive.namelist():
            if not name.startswith("word/media/"):
                continue
            data = archive.read(name)
            filename = Path(name).name
            target = OUT_DIR / filename
            target.write_bytes(data)
            count += 1
    print(f"Extracted {count} images to {OUT_DIR}")


if __name__ == "__main__":
    main()
