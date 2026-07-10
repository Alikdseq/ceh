export type CookieConsentCategory = "necessary" | "analytics" | "marketing";

export type CookieConsentState = {
  version: 1;
  updatedAt: string; // ISO
  categories: Record<CookieConsentCategory, boolean>;
};

const STORAGE_KEY = "cehsite_cookie_consent_v1";
const COOKIE_NAME = "cookie_consent_v1";
const COOKIE_MAX_AGE_DAYS = 180;
export const COOKIE_CONSENT_CHANGED_EVENT = "cehsite:cookie-consent:changed";

function nowIso() {
  return new Date().toISOString();
}

export function getDefaultConsent(): CookieConsentState {
  return {
    version: 1,
    updatedAt: nowIso(),
    categories: {
      necessary: true,
      analytics: false,
      marketing: false,
    },
  };
}

export function parseConsent(raw: string): CookieConsentState | null {
  try {
    const parsed = JSON.parse(raw) as CookieConsentState;
    if (parsed?.version !== 1) return null;
    if (!parsed.categories?.necessary) return null;
    return parsed;
  } catch {
    return null;
  }
}

export function readConsent(): CookieConsentState | null {
  if (typeof window === "undefined") return null;
  const fromStorage = window.localStorage.getItem(STORAGE_KEY);
  if (fromStorage) return parseConsent(fromStorage);

  const match = document.cookie
    .split(";")
    .map((c) => c.trim())
    .find((c) => c.startsWith(`${COOKIE_NAME}=`));
  if (!match) return null;
  const value = decodeURIComponent(match.split("=").slice(1).join("="));
  return parseConsent(value);
}

export function writeConsent(state: CookieConsentState): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state));

  const expires = new Date();
  expires.setDate(expires.getDate() + COOKIE_MAX_AGE_DAYS);
  document.cookie = [
    `${COOKIE_NAME}=${encodeURIComponent(JSON.stringify(state))}`,
    `expires=${expires.toUTCString()}`,
    "path=/",
    "samesite=lax",
  ].join("; ");

  window.dispatchEvent(new CustomEvent(COOKIE_CONSENT_CHANGED_EVENT, { detail: state }));
}

export function acceptAllConsent(): CookieConsentState {
  return {
    version: 1,
    updatedAt: nowIso(),
    categories: { necessary: true, analytics: true, marketing: true },
  };
}

export function acceptNecessaryOnlyConsent(): CookieConsentState {
  return {
    version: 1,
    updatedAt: nowIso(),
    categories: { necessary: true, analytics: false, marketing: false },
  };
}

export function normalizeConsent(next: Partial<CookieConsentState>): CookieConsentState {
  const base = getDefaultConsent();
  const categories = {
    ...base.categories,
    ...(next.categories ?? {}),
    necessary: true,
  };
  return {
    version: 1,
    updatedAt: nowIso(),
    categories,
  };
}

