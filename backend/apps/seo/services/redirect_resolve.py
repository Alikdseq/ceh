"""Unified redirect resolution: legacy CMS paths + Redirect model."""

from __future__ import annotations

import re

from apps.seo.models import Redirect
from apps.seo.services.legacy_paths import normalize_legacy_path, paths_equivalent, resolve_legacy_path

_OLD_CATALOG_SECTIONS = frozenset(
    {"contactor", "switch", "packet", "cam", "starter", "kte", "accessory"}
)
_OLD_CATALOG_RE = re.compile(r"^/catalog/([^/]+)/?", re.IGNORECASE)


def is_legacy_redirect_candidate(path: str, query: str = "") -> bool:
    """Only old CMS URL shapes should hit legacy resolver / middleware."""
    normalized = normalize_legacy_path(path)
    no_slash = normalized.rstrip("/")

    if normalized.startswith("/company/") or no_slash == "/company":
        return True
    if normalized.startswith("/files/") or no_slash == "/files":
        return True

    match = _OLD_CATALOG_RE.match(normalized) or _OLD_CATALOG_RE.match(f"{no_slash}/")
    if match:
        section = match.group(1).lower()
        if section in _OLD_CATALOG_SECTIONS:
            return True
        if query and "id=" in query:
            return True
    return False


def resolve_redirect(path: str, query: str = "") -> str | None:
    """
    Resolve a redirect target or None.

    Order: legacy CMS (if candidate) → Redirect model.
    Never returns a target equivalent to source.
    """
    if not path.startswith("/"):
        path = f"/{path}"

    if is_legacy_redirect_candidate(path, query):
        legacy_target = resolve_legacy_path(path, query)
        if legacy_target and not paths_equivalent(path, legacy_target):
            return legacy_target

    redirect = Redirect.objects.filter(old_path=path, is_active=True).first()
    if not redirect:
        redirect = Redirect.objects.filter(old_path=path.rstrip("/"), is_active=True).first()
    if not redirect and not path.endswith("/"):
        redirect = Redirect.objects.filter(old_path=f"{path}/", is_active=True).first()

    if redirect and not paths_equivalent(path, redirect.new_path):
        return redirect.new_path

    return None
