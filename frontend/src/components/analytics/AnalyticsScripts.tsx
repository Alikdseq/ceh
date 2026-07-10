"use client";

import Script from "next/script";

interface AnalyticsScriptsProps {
  yandexMetrikaId?: string;
  ga4Id?: string;
}

export function AnalyticsScripts({ yandexMetrikaId, ga4Id }: AnalyticsScriptsProps) {
  return (
    <>
      {yandexMetrikaId && (
        <>
          <Script id="yandex-metrika" strategy="afterInteractive">
            {`
              (function(m,e,t,r,i,k,a){m[i]=m[i]||function(){(m[i].a=m[i].a||[]).push(arguments)};
              m[i].l=1*new Date();
              for (var j = 0; j < document.scripts.length; j++) {if (document.scripts[j].src === r) { return; }}
              k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)})
              (window, document, "script", "https://mc.yandex.ru/metrika/tag.js", "ym");
              ym(${JSON.stringify(yandexMetrikaId)}, "init", { clickmap:true, trackLinks:true, accurateTrackBounce:true, webvisor:true });
            `}
          </Script>
          <noscript>
            <div>
              <img
                src={`https://mc.yandex.ru/watch/${yandexMetrikaId}`}
                style={{ position: "absolute", left: "-9999px" }}
                alt=""
              />
            </div>
          </noscript>
        </>
      )}
      {ga4Id && (
        <>
          <Script
            src={`https://www.googletagmanager.com/gtag/js?id=${ga4Id}`}
            strategy="afterInteractive"
          />
          <Script id="ga4-init" strategy="afterInteractive">
            {`
              window.dataLayer = window.dataLayer || [];
              function gtag(){dataLayer.push(arguments);}
              gtag('js', new Date());
              gtag('config', ${JSON.stringify(ga4Id)});
            `}
          </Script>
        </>
      )}
    </>
  );
}

/** Fire conversion goals on quote submit (STEP-104). */
export function trackQuoteSubmit(quoteNumber: string, yandexMetrikaId?: string) {
  if (typeof window === "undefined") return;
  const w = window as Window & {
    ym?: (id: number | string, action: string, goal: string) => void;
    gtag?: (...args: unknown[]) => void;
  };
  if (yandexMetrikaId) {
    try {
      w.ym?.(yandexMetrikaId, "reachGoal", "quote_submit");
    } catch {
      /* ym not loaded */
    }
  }
  try {
    w.gtag?.("event", "generate_lead", { event_category: "quote", event_label: quoteNumber });
  } catch {
    /* gtag not loaded */
  }
}
