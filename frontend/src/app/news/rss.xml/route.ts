import { getApiBase } from "@/lib/api/client";

export async function GET() {
  const res = await fetch(`${getApiBase()}/news/rss/`, { next: { revalidate: 600 } });
  const xml = await res.text();
  return new Response(xml, {
    headers: { "Content-Type": "application/rss+xml; charset=utf-8" },
  });
}
