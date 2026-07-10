"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { ChevronLeft, ChevronRight, Handshake } from "lucide-react";

import { cn } from "@/lib/utils";
import type { Partner } from "@/lib/partners";

interface PartnersCarouselProps {
  partners: Partner[];
  className?: string;
}

const NAV_BTN =
  "absolute top-1/2 z-20 hidden h-11 w-11 -translate-y-1/2 items-center justify-center rounded-full border border-border bg-card text-[var(--color-brand-blue-dark)] shadow-[0_4px_14px_rgba(0,86,132,0.12)] transition hover:border-[var(--color-brand-blue)] hover:bg-[var(--color-brand-blue)] hover:text-white disabled:cursor-not-allowed disabled:opacity-35 md:flex";

const TRACK =
  "flex gap-4 overflow-x-auto overscroll-x-contain scroll-smooth pb-1 snap-x snap-mandatory [-ms-overflow-style:none] [scrollbar-width:none] md:px-12 [&::-webkit-scrollbar]:hidden";

function PartnerCard({ partner }: { partner: Partner }) {
  return (
    <article
      className={cn(
        "group relative flex h-full min-h-[148px] w-[min(100%,280px)] shrink-0 snap-start flex-col",
        "rounded-lg border border-[var(--color-border)] bg-gradient-to-br from-card to-[var(--color-brand-blue-light)] p-5 shadow-sm",
        "transition-all duration-300 hover:border-[var(--color-brand-blue)] hover:shadow-md",
        "sm:w-[300px] lg:w-[320px]",
      )}
    >
      <div
        className="absolute inset-y-0 left-0 w-1 rounded-l-lg bg-[var(--color-brand-blue)] opacity-80 transition-opacity group-hover:opacity-100"
        aria-hidden
      />
      <div className="flex items-start gap-3 pl-2">
        <div
          className={cn(
            "flex h-10 w-10 shrink-0 items-center justify-center rounded-md",
            "bg-[var(--color-brand-blue-light)] text-[var(--color-brand-blue-dark)]",
            "transition-colors group-hover:bg-[var(--color-brand-blue)] group-hover:text-white",
          )}
        >
          <Handshake className="h-5 w-5" aria-hidden />
        </div>
        <div className="min-w-0 flex-1">
          <h3 className="font-display text-base font-bold leading-snug tracking-tight text-[var(--color-text-primary)] md:text-[1.05rem]">
            {partner.name}
          </h3>
          {partner.subtitle ? (
            <p className="mt-1 text-sm leading-snug text-muted-foreground">{partner.subtitle}</p>
          ) : null}
        </div>
      </div>
      <div className="mt-auto pt-4 pl-2">
        <span
          className={cn(
            "inline-flex items-center rounded-md px-2.5 py-1",
            "bg-[var(--color-brand-blue-light)]/80 font-mono text-xs font-medium tracking-wide",
            "text-[var(--color-brand-blue-dark)]",
            "ring-1 ring-[var(--color-brand-blue)]/15",
          )}
        >
          ИНН&nbsp;{partner.inn}
        </span>
      </div>
    </article>
  );
}

export function PartnersCarousel({ partners, className }: PartnersCarouselProps) {
  const trackRef = useRef<HTMLDivElement>(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(false);

  const updateScrollState = useCallback(() => {
    const el = trackRef.current;
    if (!el) return;
    const { scrollLeft, scrollWidth, clientWidth } = el;
    setCanScrollLeft(scrollLeft > 4);
    setCanScrollRight(scrollLeft + clientWidth < scrollWidth - 4);
  }, []);

  useEffect(() => {
    const el = trackRef.current;
    if (!el) return;

    updateScrollState();

    el.addEventListener("scroll", updateScrollState, { passive: true });
    window.addEventListener("resize", updateScrollState);

    return () => {
      el.removeEventListener("scroll", updateScrollState);
      window.removeEventListener("resize", updateScrollState);
    };
  }, [updateScrollState, partners.length]);

  const scroll = (direction: "left" | "right") => {
    const el = trackRef.current;
    if (!el) return;
    const step = Math.max(el.clientWidth * 0.85, 280);
    el.scrollBy({ left: direction === "left" ? -step : step, behavior: "smooth" });
  };

  if (partners.length === 0) return null;

  return (
    <div className={cn("relative", className)}>
      <div
        className={cn(
          "pointer-events-none absolute inset-y-0 left-0 z-10 w-8 bg-gradient-to-r from-muted/90 to-transparent",
          "hidden md:block",
          !canScrollLeft && "opacity-0",
        )}
        aria-hidden
      />
      <div
        className={cn(
          "pointer-events-none absolute inset-y-0 right-0 z-10 w-8 bg-gradient-to-l from-muted/90 to-transparent",
          "hidden md:block",
          !canScrollRight && "opacity-0",
        )}
        aria-hidden
      />

      <button
        type="button"
        onClick={() => scroll("left")}
        disabled={!canScrollLeft}
        aria-label="Прокрутить партнёров влево"
        className={cn(NAV_BTN, "left-0")}
      >
        <ChevronLeft className="h-5 w-5" aria-hidden />
      </button>

      <button
        type="button"
        onClick={() => scroll("right")}
        disabled={!canScrollRight}
        aria-label="Прокрутить партнёров вправо"
        className={cn(NAV_BTN, "right-0")}
      >
        <ChevronRight className="h-5 w-5" aria-hidden />
      </button>

      <div ref={trackRef} className={TRACK} role="list" aria-label="Список партнёров">
        {partners.map((partner) => (
          <div key={partner.id} role="listitem" className="flex">
            <PartnerCard partner={partner} />
          </div>
        ))}
      </div>

      <p className="mt-3 text-center text-xs text-muted-foreground md:hidden">
        Листайте влево и вправо
      </p>
    </div>
  );
}
