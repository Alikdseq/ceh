/** Shared robots.txt body for ekontaktor.ru (frontend route + backend API). */

const COMMON_DISALLOWS = [
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
] as const;

const YANDEX_CLEAN_PARAMS = [
  "utm_source&utm_medium&utm_campaign&utm_content&utm_term&yclid&gbid&from /",
  "page&page_size&ordering&view&current&coil&coil_min&coil_max&poles&execution&product_type&series&climate&application&doc&type&current_min&current_max /catalog/",
  "variant /catalog/",
] as const;

function formatBlock(userAgent: string, disallows: readonly string[], extras: string[] = []): string {
  const lines = [`User-agent: ${userAgent}`, "Allow: /", ...disallows.map((path) => `Disallow: ${path}`), ...extras];
  return lines.join("\n");
}

export function buildRobotsTxt(siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://www.ekontaktor.ru"): string {
  const base = siteUrl.replace(/\/$/, "");
  const host = new URL(base).host;

  const universal = formatBlock("*", COMMON_DISALLOWS);
  const yandexExtras = [`Host: ${host}`, ...YANDEX_CLEAN_PARAMS.map((rule) => `Clean-param: ${rule}`)];
  const yandex = formatBlock("Yandex", COMMON_DISALLOWS, yandexExtras);

  return [
    "# robots.txt — https://www.ekontaktor.ru/",
    "# Service pages and faceted URLs are noindex via meta; rules below save crawl budget.",
    universal,
    "",
    yandex,
    "",
    `Sitemap: ${base}/sitemap.xml`,
    "",
  ].join("\n");
}
