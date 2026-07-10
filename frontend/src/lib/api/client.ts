export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public path: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export function getApiBase(): string {
  // Browser: same-origin proxy (/api → backend) avoids CORS and CSRF issues.
  if (typeof window !== "undefined") {
    return "/api/v1";
  }
  const internal = process.env.INTERNAL_API_URL?.replace(/\/$/, "");
  if (internal) return internal;
  return (process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1").replace(/\/$/, "");
}

function normalizeApiPath(path: string): string {
  const normalized = path.startsWith("/") ? path : `/${path}`;
  if (normalized.includes("?")) return normalized;
  return normalized.endsWith("/") ? normalized : `${normalized}/`;
}

function buildUrl(path: string, params?: URLSearchParams): string {
  const normalized = normalizeApiPath(path);
  const base = `${getApiBase()}${normalized}`;
  const qs = params?.toString();
  if (!qs) return base;
  const separator = base.includes("?") ? "&" : "?";
  return `${base}${separator}${qs}`;
}

export async function fetchApi<T>(
  path: string,
  init?: RequestInit & { revalidate?: number; params?: URLSearchParams; cache?: RequestCache },
): Promise<T> {
  const { revalidate = 3600, params, cache, ...rest } = init ?? {};
  const url = params ? buildUrl(path, params) : buildUrl(path);
  let res: Response;
  try {
    res = await fetch(url, {
      ...rest,
      ...(cache ? { cache } : { next: { revalidate } }),
    });
  } catch {
    throw new ApiError(`API unreachable: ${path}`, 0, path);
  }
  if (!res.ok) {
    throw new ApiError(`API ${path}: ${res.status}`, res.status, path);
  }
  return res.json() as Promise<T>;
}

/** Client-side fetch (no Next.js cache) for public API calls from the browser. */
export async function fetchApiClient<T>(
  path: string,
  init?: RequestInit & { params?: URLSearchParams },
): Promise<T> {
  const { params, headers, ...rest } = init ?? {};
  const url = params ? buildUrl(path, params) : buildPath(path);
  const hasBody = rest.body != null && rest.body !== "";
  const res = await fetch(url, {
    method: rest.method ?? "GET",
    body: rest.body,
    signal: rest.signal,
    cache: "no-store",
    credentials: "omit",
    headers: {
      Accept: "application/json",
      ...(hasBody ? { "Content-Type": "application/json" } : {}),
      ...(headers ?? {}),
    },
  });
  if (!res.ok) {
    let detail = `API ${path}: ${res.status}`;
    try {
      const body = (await res.json()) as { detail?: string };
      if (body.detail) detail = body.detail;
    } catch {
      /* ignore */
    }
    throw new ApiError(detail, res.status, path);
  }
  if (res.status === 204) {
    return undefined as T;
  }
  return res.json() as Promise<T>;
}

function buildPath(path: string): string {
  return buildUrl(path);
}

/** Client fetch with cart session header + cookie credentials. */
export async function fetchCartApi<T>(path: string, init?: RequestInit): Promise<{ data: T; response: Response }> {
  const { cartSessionHeaders, syncCartSessionFromResponse } = await import("@/lib/cart-session");
  const url = buildUrl(path);
  const res = await fetch(url, {
    ...init,
    cache: "no-store",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...cartSessionHeaders(),
      ...(init?.headers ?? {}),
    },
  });
  syncCartSessionFromResponse(res);
  if (!res.ok) {
    let detail = `API ${path}: ${res.status}`;
    try {
      const body = (await res.json()) as { detail?: string };
      if (body.detail) detail = body.detail;
    } catch {
      /* ignore */
    }
    throw new ApiError(detail, res.status, path);
  }
  const data = (await res.json()) as T;
  return { data, response: res };
}

export function toSearchParams(params?: Record<string, string | number | boolean>): URLSearchParams {
  const search = new URLSearchParams();
  if (!params) return search;
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== "") search.set(key, String(value));
  });
  return search;
}
