const SESSION_KEY = "cart_session";

export function getCartSession(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(SESSION_KEY);
}

export function setCartSession(session: string): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(SESSION_KEY, session);
}

export function cartSessionHeaders(): HeadersInit {
  const session = getCartSession();
  return session ? { "X-Cart-Session": session } : {};
}

export function syncCartSessionFromResponse(res: Response): void {
  const header = res.headers.get("X-Cart-Session");
  if (header) setCartSession(header);
}
