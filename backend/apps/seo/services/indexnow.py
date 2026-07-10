"""IndexNow URL submission for Yandex and Bing."""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.parse
import urllib.request

from django.conf import settings

logger = logging.getLogger(__name__)

INDEXNOW_ENDPOINTS = (
    "https://yandex.com/indexnow",
    "https://api.indexnow.org/indexnow",
)


def _frontend_base() -> str:
    return getattr(settings, "FRONTEND_URL", "http://localhost:3000").rstrip("/")


def _absolute_urls(urls: list[str]) -> list[str]:
    base = _frontend_base()
    result: list[str] = []
    for url in urls:
        if url.startswith("http://") or url.startswith("https://"):
            result.append(url)
        else:
            path = url if url.startswith("/") else f"/{url}"
            result.append(f"{base}{path}")
    return result


def submit_indexnow_urls(urls: list[str]) -> dict:
    """POST changed URLs to IndexNow endpoints. Returns summary dict."""
    if not getattr(settings, "INDEXNOW_ENABLED", False):
        return {"skipped": True, "reason": "INDEXNOW_ENABLED is false"}

    key = getattr(settings, "INDEXNOW_KEY", "").strip()
    if not key:
        return {"skipped": True, "reason": "INDEXNOW_KEY is empty"}

    absolute = _absolute_urls(urls)
    if not absolute:
        return {"skipped": True, "reason": "no urls"}

    host = urllib.parse.urlparse(_frontend_base()).netloc
    payload = json.dumps(
        {"host": host, "key": key, "urlList": absolute[:10_000]},
        ensure_ascii=False,
    ).encode("utf-8")

    results: dict[str, int | str] = {"submitted": len(absolute), "endpoints": {}}
    for endpoint in INDEXNOW_ENDPOINTS:
        req = urllib.request.Request(
            endpoint,
            data=payload,
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                results["endpoints"][endpoint] = resp.status
        except urllib.error.HTTPError as exc:
            results["endpoints"][endpoint] = exc.code
            logger.warning("IndexNow HTTP error for %s: %s", endpoint, exc.code)
        except OSError as exc:
            results["endpoints"][endpoint] = str(exc)
            logger.warning("IndexNow request failed for %s: %s", endpoint, exc)

    return results
