import type { Metadata } from "next";
import Link from "next/link";
import { Suspense } from "react";
import { CheckCircle2 } from "lucide-react";

import { QuoteSuccessAnalytics } from "@/components/analytics/QuoteSuccessAnalytics";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { Button } from "@/components/ui/button";
import { getSiteSettings } from "@/lib/api";

export const metadata: Metadata = {
  title: "Заявка отправлена",
  robots: { index: false, follow: false },
};

interface SuccessPageProps {
  searchParams: Promise<{ number?: string }>;
}

export default async function OrderSuccessPage({ searchParams }: SuccessPageProps) {
  const { number } = await searchParams;
  const settings = await getSiteSettings();

  return (
    <div className="section-py">
      <Suspense fallback={null}>
        <QuoteSuccessAnalytics yandexMetrikaId={settings?.yandex_metrika_id} />
      </Suspense>
      <div className="container-page max-w-xl">
        <Breadcrumbs
          items={[
            { label: "Главная", href: "/" },
            { label: "Заявка отправлена" },
          ]}
          className="mb-6"
        />

        <div className="rounded-lg border bg-card p-8 text-center">
          <CheckCircle2 className="mx-auto h-14 w-14 text-primary" />
          <h1 className="mt-4 font-display text-2xl font-bold">Заявка принята</h1>
          {number ? (
            <p className="mt-3 text-lg">
              Номер заявки: <strong className="text-primary">{number}</strong>
            </p>
          ) : (
            <p className="mt-3 text-muted-foreground">Мы получили ваш запрос.</p>
          )}
          <p className="mt-4 text-sm text-muted-foreground">
            Подтверждение отправлено на указанный email. Менеджер свяжется с вами в ближайшее время.
          </p>
          <div className="mt-8 flex flex-wrap justify-center gap-3">
            <Button asChild>
              <Link href="/catalog/">В каталог</Link>
            </Button>
            <Button asChild variant="outline">
              <Link href="/">На главную</Link>
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
