"use client";

import { useEffect } from "react";
import { useSearchParams } from "next/navigation";

import { trackQuoteSubmit } from "@/components/analytics/AnalyticsScripts";

interface QuoteSuccessAnalyticsProps {
  yandexMetrikaId?: string;
}

export function QuoteSuccessAnalytics({ yandexMetrikaId }: QuoteSuccessAnalyticsProps) {
  const searchParams = useSearchParams();
  const number = searchParams.get("number");

  useEffect(() => {
    if (number) trackQuoteSubmit(number, yandexMetrikaId);
  }, [number, yandexMetrikaId]);

  return null;
}
