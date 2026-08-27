"""Fix uploaded product image orientation from EXIF metadata."""

from __future__ import annotations

import logging
from io import BytesIO

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

logger = logging.getLogger(__name__)


def normalize_uploaded_image(file_field) -> bool:
    """
    Apply EXIF orientation and save pixels upright (no CSS rotation needed).

    Returns True when the stored file was rewritten.
    """
    if not file_field or not file_field.name:
        return False
    if not default_storage.exists(file_field.name):
        return False

    try:
        from PIL import Image, ImageOps
    except ImportError:
        return False

    try:
        with default_storage.open(file_field.name, "rb") as handle:
            img = Image.open(handle)
            img.load()
            corrected = ImageOps.exif_transpose(img)
            if corrected is img:
                return False

            buffer = BytesIO()
            fmt = (img.format or "JPEG").upper()
            save_kwargs: dict = {}
            if fmt in ("JPEG", "JPG"):
                save_kwargs["quality"] = 92
                if corrected.mode in ("RGBA", "P"):
                    corrected = corrected.convert("RGB")
                fmt = "JPEG"
            elif fmt == "PNG":
                save_kwargs["optimize"] = True

            corrected.save(buffer, format=fmt, **save_kwargs)
            buffer.seek(0)
            default_storage.save(file_field.name, ContentFile(buffer.read()))
            return True
    except Exception:
        logger.warning("Could not normalize image orientation for %s", file_field.name, exc_info=True)
        return False
