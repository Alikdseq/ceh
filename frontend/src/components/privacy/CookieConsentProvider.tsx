"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import {
  acceptAllConsent,
  acceptNecessaryOnlyConsent,
  getDefaultConsent,
  normalizeConsent,
  readConsent,
  type CookieConsentState,
  writeConsent,
} from "@/lib/cookie-consent";

export type CookieConsentContextValue = {
  consent: CookieConsentState;
  hasDecision: boolean;
  setConsent: (next: CookieConsentState) => void;
  openSettings: () => void;
};

const OPEN_SETTINGS_EVENT = "cehsite:cookie-consent:open-settings";

export function requestOpenCookieSettings() {
  if (typeof window === "undefined") return;
  window.dispatchEvent(new Event(OPEN_SETTINGS_EVENT));
}

export function CookieConsentProvider({
  children,
  className,
  onConsentChange,
}: {
  children?: React.ReactNode;
  className?: string;
  onConsentChange?: (consent: CookieConsentState) => void;
}) {
  const [consent, setConsentState] = useState<CookieConsentState>(() => {
    if (typeof window === "undefined") return getDefaultConsent();
    return readConsent() ?? getDefaultConsent();
  });
  const [hasDecision, setHasDecision] = useState(() => {
    if (typeof window === "undefined") return false;
    return readConsent() !== null;
  });
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    const handler = () => setSettingsOpen(true);
    window.addEventListener(OPEN_SETTINGS_EVENT, handler);
    return () => window.removeEventListener(OPEN_SETTINGS_EVENT, handler);
  }, []);

  const api = useMemo<CookieConsentContextValue>(() => {
    return {
      consent,
      hasDecision,
      setConsent: (next) => {
        writeConsent(next);
        setConsentState(next);
        setHasDecision(true);
        onConsentChange?.(next);
      },
      openSettings: () => setSettingsOpen(true),
    };
  }, [consent, hasDecision, onConsentChange]);

  function acceptAll() {
    api.setConsent(acceptAllConsent());
    setSettingsOpen(false);
  }

  function acceptNecessaryOnly() {
    api.setConsent(acceptNecessaryOnlyConsent());
    setSettingsOpen(false);
  }

  function saveSelection(next: Partial<CookieConsentState>) {
    api.setConsent(normalizeConsent(next));
    setSettingsOpen(false);
  }

  return (
    <>
      {children}

      {!hasDecision && mounted ? (
        <div
          className={cn(
            "fixed inset-x-0 bottom-0 z-[60] border-t border-[var(--color-border)] bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/85",
            className,
          )}
          role="dialog"
          aria-label="Настройки cookie"
        >
          <div className="container-page flex flex-col gap-3 py-4 md:flex-row md:items-center md:justify-between">
            <div className="max-w-3xl text-sm text-foreground">
              <p className="font-medium">Файлы cookie</p>
              <p className="mt-1 text-muted-foreground">
                Мы используем cookie для работы сайта, а также для аналитики и улучшения сервиса. Вы можете принять все cookie
                или настроить выбор. Подробнее — в{" "}
                <Link href="/cookies/" className="text-primary underline underline-offset-2">
                  Политике cookie
                </Link>{" "}
                и{" "}
                <Link href="/privacy/" className="text-primary underline underline-offset-2">
                  Политике обработки персональных данных
                </Link>
                .
              </p>
            </div>
            <div className="flex flex-wrap gap-2">
              <Button type="button" variant="outline" onClick={() => setSettingsOpen(true)}>
                Настроить
              </Button>
              <Button type="button" variant="outline" onClick={acceptNecessaryOnly}>
                Только необходимые
              </Button>
              <Button type="button" variant="accent" onClick={acceptAll}>
                Принять все
              </Button>
            </div>
          </div>
        </div>
      ) : null}

      {settingsOpen ? (
        <div className="fixed inset-0 z-[70] flex items-end justify-center bg-black/40 p-4 md:items-center" role="dialog" aria-modal>
          <div className="w-full max-w-xl rounded-lg border border-[var(--color-border)] bg-white p-5 shadow-lg">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-base font-semibold">Настройки cookie</p>
                <p className="mt-1 text-sm text-muted-foreground">
                  Необходимые cookie всегда включены. Аналитические и маркетинговые можно отключить.
                </p>
              </div>
              <Button type="button" variant="ghost" onClick={() => setSettingsOpen(false)} aria-label="Закрыть">
                Закрыть
              </Button>
            </div>

            <div className="mt-4 space-y-3 text-sm">
              <label className="flex items-start gap-3">
                <input type="checkbox" checked disabled className="mt-1 h-4 w-4 rounded border-input" />
                <span>
                  <span className="font-medium">Необходимые</span>
                  <span className="block text-muted-foreground">
                    Обеспечивают корректную работу сайта и безопасность.
                  </span>
                </span>
              </label>

              <label className="flex items-start gap-3">
                <input
                  type="checkbox"
                  checked={consent.categories.analytics}
                  onChange={(e) => setConsentState((s) => normalizeConsent({ categories: { ...s.categories, analytics: e.target.checked } }))}
                  className="mt-1 h-4 w-4 rounded border-input"
                />
                <span>
                  <span className="font-medium">Аналитические</span>
                  <span className="block text-muted-foreground">
                    Помогают понять, как используется сайт (например, Яндекс.Метрика).
                  </span>
                </span>
              </label>

              <label className="flex items-start gap-3">
                <input
                  type="checkbox"
                  checked={consent.categories.marketing}
                  onChange={(e) => setConsentState((s) => normalizeConsent({ categories: { ...s.categories, marketing: e.target.checked } }))}
                  className="mt-1 h-4 w-4 rounded border-input"
                />
                <span>
                  <span className="font-medium">Маркетинговые</span>
                  <span className="block text-muted-foreground">
                    Используются для персонализации и рекламных измерений (если применимо).
                  </span>
                </span>
              </label>
            </div>

            <div className="mt-5 flex flex-wrap gap-2">
              <Button type="button" variant="outline" onClick={acceptNecessaryOnly}>
                Только необходимые
              </Button>
              <Button type="button" variant="outline" onClick={acceptAll}>
                Принять все
              </Button>
              <Button type="button" variant="accent" onClick={() => saveSelection(consent)}>
                Сохранить выбор
              </Button>
            </div>

            <p className="mt-3 text-xs text-muted-foreground">
              Вы всегда можете изменить выбор через ссылку «Настройки cookie» внизу сайта.
            </p>
          </div>
        </div>
      ) : null}
    </>
  );
}

