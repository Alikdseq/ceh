import { getApiBase } from "@/lib/api/client";

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const res = await fetch(`${getApiBase()}/seo/sitemap.xml`, {
      next: { revalidate: 3600 },
    });
    if (!res.ok) throw new Error(`sitemap ${res.status}`);
    const body = await res.text();
    return new Response(body, {
      headers: { "Content-Type": "application/xml; charset=utf-8" },
    });
  } catch {
    const fallback = `<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"></urlset>`;
    return new Response(fallback, {
      headers: { "Content-Type": "application/xml; charset=utf-8" },
    });
  }
}
