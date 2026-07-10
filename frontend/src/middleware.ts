import { NextResponse, type NextRequest } from "next/server";

const API_BASE = (process.env.INTERNAL_API_URL || process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1").replace(/\/$/, "");

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  if (
    pathname.startsWith("/api") ||
    pathname.startsWith("/_next") ||
    pathname.includes(".")
  ) {
    return NextResponse.next();
  }

  try {
    const res = await fetch(
      `${API_BASE}/redirects/resolve/?path=${encodeURIComponent(pathname)}`,
      { next: { revalidate: 300 } },
    );
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
    "/((?!_next/static|_next/image|_next/webpack-hmr|favicon.ico|manifest.webmanifest|photos/|tovar/|placeholder-product.svg|.*\\.(?:svg|png|jpg|jpeg|webp|ico|woff2?|css|js)$).*)",
  ],
};
