"""robots.txt body — keep in sync with frontend/src/lib/robots-txt.ts"""

from __future__ import annotations

from django.conf import settings

COMMON_DISALLOWS = (
    "/manage/",
    "/api/",
    "/_next/",
    "/cart",
    "/cart/",
    "/compare",
    "/compare/",
    "/order/",
    "/dev/",
    "/search",
    "/subscribe/confirm/",
    "/unsubscribe/",
    "/*?variant=",
)

YANDEX_CLEAN_PARAMS = (
    "utm_source&utm_medium&utm_campaign&utm_content&utm_term&yclid&gbid&from /",
    "page&page_size&ordering&view&current&coil&coil_min&coil_max&poles&execution"
    "&product_type&series&climate&application&doc&type&current_min&current_max /catalog/",
    "variant /catalog/",
)


def _format_block(user_agent: str, disallows: tuple[str, ...], extras: tuple[str, ...] = ()) -> str:
    lines = [f"User-agent: {user_agent}", "Allow: /"]
    lines.extend(f"Disallow: {path}" for path in disallows)
    lines.extend(extras)
    return "\n".join(lines)


def build_robots_txt() -> str:
    base = getattr(settings, "FRONTEND_URL", "http://localhost:3000").rstrip("/")
    host = base.replace("https://", "").replace("http://", "").split("/")[0]

    universal = _format_block("*", COMMON_DISALLOWS)
    yandex_extras = (f"Host: {host}", *(f"Clean-param: {rule}" for rule in YANDEX_CLEAN_PARAMS))
    yandex = _format_block("Yandex", COMMON_DISALLOWS, yandex_extras)

    return (
        "# robots.txt — https://www.ekontaktor.ru/\n"
        "# Service pages and faceted URLs are noindex via meta; rules below save crawl budget.\n"
        f"{universal}\n\n"
        f"{yandex}\n\n"
        f"Sitemap: {base}/sitemap.xml\n"
    )
