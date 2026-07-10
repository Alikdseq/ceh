import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

/** Backend origin without /api/v1 suffix (e.g. http://backend:8000). */
export function getBackendOrigin(): string {
  const raw =
    process.env.INTERNAL_API_URL ||
    process.env.NEXT_PUBLIC_API_URL ||
    "http://127.0.0.1:8000/api/v1";
  return raw.replace(/\/api\/v1\/?$/, "").replace(/\/$/, "");
}

/** Django expects trailing slashes; Next rewrites strip them and cause 301 loops. */
export function buildBackendApiUrl(pathname: string, search: string): string {
  const origin = getBackendOrigin();
  const normalizedPath = pathname.endsWith("/") ? pathname : `${pathname}/`;
  return `${origin}${normalizedPath}${search}`;
}

const HOP_BY_HOP = new Set([
  "connection",
  "keep-alive",
  "proxy-authenticate",
  "proxy-authorization",
  "te",
  "trailers",
  "transfer-encoding",
  "upgrade",
  "host",
]);

export async function proxyApiRequest(request: NextRequest): Promise<NextResponse> {
  const targetUrl = buildBackendApiUrl(request.nextUrl.pathname, request.nextUrl.search);

  const headers = new Headers();
  request.headers.forEach((value, key) => {
    if (HOP_BY_HOP.has(key.toLowerCase())) return;
    headers.set(key, value);
  });

  const method = request.method.toUpperCase();
  const init: RequestInit = {
    method,
    headers,
    redirect: "manual",
  };

  if (method !== "GET" && method !== "HEAD") {
    init.body = await request.arrayBuffer();
  }

  let backendResponse: Response;
  try {
    backendResponse = await fetch(targetUrl, init);
  } catch {
    return NextResponse.json({ detail: "Backend API unreachable" }, { status: 502 });
  }

  const responseHeaders = new Headers();
  backendResponse.headers.forEach((value, key) => {
    if (HOP_BY_HOP.has(key.toLowerCase())) return;
    responseHeaders.set(key, value);
  });

  return new NextResponse(backendResponse.body, {
    status: backendResponse.status,
    statusText: backendResponse.statusText,
    headers: responseHeaders,
  });
}
