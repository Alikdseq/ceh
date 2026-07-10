import { getSiteSettings } from "@/lib/api";
import { AnalyticsGate } from "@/components/analytics/AnalyticsGate";

export async function AnalyticsProvider() {
  const settings = await getSiteSettings();
  const extended = settings as { yandex_metrika_id?: string; ga4_id?: string } | null;
  if (!extended?.yandex_metrika_id && !extended?.ga4_id) return null;
  return (
    <AnalyticsGate
      yandexMetrikaId={extended.yandex_metrika_id || undefined}
      ga4Id={extended.ga4_id || undefined}
    />
  );
}
