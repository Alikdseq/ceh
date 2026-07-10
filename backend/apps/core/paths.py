"""Resolve data files on host and in Docker (/data mount)."""

from pathlib import Path

from django.conf import settings


def resolve_data_file(raw: str, default_name: str = "pricelist.csv") -> Path:
    """
    Find a file under data/ on the host or at /data/ inside Docker.
    Returns the first existing path, or the original Path if none found.
    """
    path = Path(raw)
    if path.is_file():
        return path

    filename = path.name if path.name else default_name
    repo_root = Path(settings.BASE_DIR).parent

    for candidate in (
        Path("/data") / filename,
        repo_root / "data" / filename,
        Path(settings.BASE_DIR) / "data" / filename,
        repo_root / filename,
    ):
        if candidate.is_file():
            return candidate

    return path
