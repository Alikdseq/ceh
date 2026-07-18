import { NextResponse, type NextRequest } from "next/server";

const API_BASE = (process.env.INTERNAL_API_URL || process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1").replace(/\/$/, "");

/** Old CMS paths and dotted legacy file URLs must still hit redirect resolver. */
function shouldResolveRedirect(pathname: string): boolean {
  if (pathname.startsWith("/company/") || pathname.startsWith("/files/")) {
    return true;
  }
  if (pathname.startsWith("/catalog/") && !pathname.includes(".")) {
    return true;
  }
  if (pathname.includes(".")) {
    return false;
  }
  return true;
}

export async function middleware(request: NextRequest) {
  const { pathname, search } = request.nextUrl;

  if (
    pathname.startsWith("/api") ||
    pathname.startsWith("/_next") ||
    pathname.startsWith("/photos/") ||
    pathname.startsWith("/tovar/") ||
    !shouldResolveRedirect(pathname)
  ) {
    return NextResponse.next();
  }

  const lookupPath = pathname.endsWith("/") ? pathname : `${pathname}/`;
  const query = search.startsWith("?") ? search.slice(1) : search;

  try {
    const params = new URLSearchParams({ path: lookupPath });
    if (query) {
      params.set("query", query);
    }
    const res = await fetch(`${API_BASE}/redirects/resolve/?${params.toString()}`, {
      next: { revalidate: 300 },
    });
    if (res.ok) {
      const data = (await res.json()) as { new_path?: string | null };
      if (data.new_path) {
        return NextResponse.redirect(new URL(data.new_path, request.url), 301);
      }
    }
  } catch {
    /* API unavailable — continue */
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/((?!_next/static|_next/image|_next/webpack-hmr|favicon.ico|manifest.webmanifest|placeholder-product.svg|.*\\.(?:svg|png|jpg|jpeg|webp|ico|woff2?|css|js)$).*)",
  ],
};
