"""Public URLs for uploaded media (avoid internal Docker hostnames in API JSON)."""
from __future__ import annotations

from urllib.parse import urlparse

from django.conf import settings

_INTERNAL_HOSTS = frozenset({"backend", "localhost", "127.0.0.1"})


def _frontend_base() -> str:
    return getattr(settings, "FRONTEND_URL", "http://localhost:3000").rstrip("/")


def _is_internal_absolute(url: str) -> bool:
    try:
        parsed = urlparse(url)
    except ValueError:
        return False
    if parsed.scheme not in ("http", "https"):
        return False
    return (parsed.hostname or "") in _INTERNAL_HOSTS


def public_media_url(url: str | None, request=None) -> str | None:
    """
    Return a browser-reachable media URL.

    SSR and internal API calls use Host ``backend:8000``; ``build_absolute_uri`` then
    embeds that hostname in HTML. Prefer ``FRONTEND_URL`` (same origin as /media/ on nginx).
    """
    if not url:
        return url

    path = url
    if hasattr(url, "url"):
        path = url.url  # type: ignore[union-attr]

    path = str(path)
    if path.startswith(("http://", "https://")):
        if _is_internal_absolute(path):
            parsed = urlparse(path)
            path = parsed.path or "/"
            if parsed.query:
                path = f"{path}?{parsed.query}"
        else:
            return path

    if not path.startswith("/"):
        path = f"/{path}"

    if request is not None:
        absolute = request.build_absolute_uri(path)
        if not _is_internal_absolute(absolute):
            return absolute

    return f"{_frontend_base()}{path}"
