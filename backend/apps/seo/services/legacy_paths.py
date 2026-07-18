"""Resolve legacy ekontaktor.ru CMS URLs (/company/*, /catalog/*/?id=, /files/*)."""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from urllib.parse import parse_qs

import yaml
from django.conf import settings

_LEGACY_PATH_RE = re.compile(r"^/catalog/([^/]+)/?", re.IGNORECASE)


def _repo_root() -> Path:
    return Path(settings.BASE_DIR).parent


def _legacy_yaml_path() -> Path:
    for candidate in (
        _repo_root() / "data" / "legacy_site.yaml",
        Path("/data/legacy_site.yaml"),
    ):
        if candidate.is_file():
            return candidate
    return _repo_root() / "data" / "legacy_site.yaml"


@lru_cache(maxsize=1)
def _load_legacy_config() -> dict:
    path = _legacy_yaml_path()
    if not path.is_file():
        return {"exact_paths": {}, "prefix_paths": {}, "catalog_sections": {}, "catalog_ids": {}}
    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return {
        "exact_paths": data.get("exact_paths") or {},
        "prefix_paths": data.get("prefix_paths") or {},
        "catalog_sections": data.get("catalog_sections") or {},
        "catalog_ids": {str(k): v for k, v in (data.get("catalog_ids") or {}).items()},
    }


def normalize_legacy_path(path: str) -> str:
    if not path:
        return "/"
    if not path.startswith("/"):
        path = f"/{path}"
    path = path.split("?", 1)[0]
    if path != "/" and not path.endswith("/"):
        path = f"{path}/"
    return path


def resolve_legacy_path(path: str, query: str = "") -> str | None:
    """
    Map old CMS paths to new site URLs.

    Handles:
    - /company/news/?id=98 → /news/
    - /company/dilers/ → /partners/
    - /catalog/contactor/?id=19 → category page
    - /files/cat/foo.doc → /catalog/
    """
    normalized = normalize_legacy_path(path)
    config = _load_legacy_config()
    exact: dict[str, str] = config["exact_paths"]

    if normalized in exact:
        return exact[normalized]
    no_slash = normalized.rstrip("/")
    if no_slash in exact:
        return exact[no_slash]

    for prefix, target in sorted(config["prefix_paths"].items(), key=lambda item: -len(item[0])):
        prefix_norm = normalize_legacy_path(prefix)
        if normalized.startswith(prefix_norm) or no_slash.startswith(prefix.rstrip("/")):
            return target

    match = _LEGACY_PATH_RE.match(normalized) or _LEGACY_PATH_RE.match(f"{no_slash}/")
    if match:
        section = match.group(1).lower()
        params = parse_qs(query or "")
        legacy_id = (params.get("id") or [None])[0]
        if legacy_id and legacy_id in config["catalog_ids"]:
            return config["catalog_ids"][legacy_id]
        section_target = config["catalog_sections"].get(section)
        if section_target:
            return section_target
        return "/catalog/"

    return None


def collect_legacy_redirect_pairs() -> list[tuple[str, str]]:
    """Static legacy paths for bulk Redirect sync (query-string URLs resolved dynamically)."""
    config = _load_legacy_config()
    pairs: list[tuple[str, str]] = []
    seen: set[str] = set()

    for old, new in config["exact_paths"].items():
        old_norm = normalize_legacy_path(old).rstrip("/")
        if old_norm in seen:
            continue
        seen.add(old_norm)
        pairs.append((old_norm, normalize_legacy_path(new)))

    for prefix, new in config["prefix_paths"].items():
        old_norm = normalize_legacy_path(prefix).rstrip("/")
        if old_norm in seen:
            continue
        seen.add(old_norm)
        pairs.append((old_norm, normalize_legacy_path(new)))

    for section, new in config["catalog_sections"].items():
        old_norm = f"/catalog/{section}"
        if old_norm in seen:
            continue
        seen.add(old_norm)
        pairs.append((old_norm, normalize_legacy_path(new)))

    return sorted(pairs, key=lambda item: item[0])
