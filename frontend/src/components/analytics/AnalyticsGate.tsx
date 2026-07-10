"use client";

import { useEffect, useState } from "react";

import { AnalyticsScripts } from "@/components/analytics/AnalyticsScripts";
import { COOKIE_CONSENT_CHANGED_EVENT, readConsent, type CookieConsentState } from "@/lib/cookie-consent";

export function AnalyticsGate({
  yandexMetrikaId,
  ga4Id,
}: {
  yandexMetrikaId?: string;
  ga4Id?: string;
}) {
  const [consent, setConsent] = useState<CookieConsentState | null>(null);

  useEffect(() => {
    setConsent(readConsent());
    const onStorage = () => setConsent(readConsent());
    const onChanged = () => setConsent(readConsent());
    window.addEventListener("storage", onStorage);
    window.addEventListener(COOKIE_CONSENT_CHANGED_EVENT, onChanged as EventListener);
    return () => {
      window.removeEventListener("storage", onStorage);
      window.removeEventListener(COOKIE_CONSENT_CHANGED_EVENT, onChanged as EventListener);
    };
  }, []);

  if (!yandexMetrikaId && !ga4Id) return null;
  if (!consent?.categories.analytics) return null;

  return <AnalyticsScripts yandexMetrikaId={yandexMetrikaId} ga4Id={ga4Id} />;
}

