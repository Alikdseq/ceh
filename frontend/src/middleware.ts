import { NextResponse, type NextRequest } from "next/server";

const API_BASE = (process.env.INTERNAL_API_URL || process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1").replace(/\/$/, "");

const OLD_CATALOG_SECTIONS = new Set([
  "contactor",
  "switch",
  "packet",
  "cam",
  "starter",
  "kte",
  "accessory",
]);

function normalizePath(path: string): string {
  if (path !== "/" && !path.endsWith("/")) {
    return `${path}/`;
  }
  return path;
}

/** Only legacy CMS URL shapes hit redirect resolver (avoids loops on /news/, /partners/, etc.). */
function shouldResolveRedirect(pathname: string, query: string): boolean {
  if (pathname.startsWith("/company/") || pathname === "/company") {
    return true;
  }
  if (pathname.startsWith("/files/") || pathname === "/files") {
    return true;
  }
  const catalogMatch = pathname.match(/^\/catalog\/([^/]+)\/?$/i);
  if (catalogMatch) {
    const section = catalogMatch[1].toLowerCase();
    if (OLD_CATALOG_SECTIONS.has(section)) {
      return true;
    }
    if (query.includes("id=")) {
      return true;
    }
  }
  return false;
}

export async function middleware(request: NextRequest) {
  const { pathname, search } = request.nextUrl;

  if (
    pathname.startsWith("/api") ||
    pathname.startsWith("/_next") ||
    pathname.startsWith("/photos/") ||
    pathname.startsWith("/tovar/")
  ) {
    return NextResponse.next();
  }

  const query = search.startsWith("?") ? search.slice(1) : search;
  if (!shouldResolveRedirect(pathname, query)) {
    return NextResponse.next();
  }

  const lookupPath = normalizePath(pathname);

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
      if (data.new_path && !pathsEquivalent(pathname, data.new_path)) {
        return NextResponse.redirect(new URL(data.new_path, request.url), 301);
      }
    }
  } catch {
    /* API unavailable — continue */
  }

  return NextResponse.next();
}

function pathsEquivalent(source: string, target: string): boolean {
  return normalizePath(source).replace(/\/+$/, "") === normalizePath(target).replace(/\/+$/, "");
}

export const config = {
  matcher: [
    "/((?!_next/static|_next/image|_next/webpack-hmr|favicon.ico|manifest.webmanifest|placeholder-product.svg|.*\\.(?:svg|png|jpg|jpeg|webp|ico|woff2?|css|js)$).*)",
  ],
};
