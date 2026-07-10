import type { Metadata } from "next";
import { Suspense } from "react";

import { ComparePageClient } from "@/components/compare/ComparePageClient";

export const metadata: Metadata = {
  title: "Сравнение товаров",
  robots: { index: false, follow: true },
};

export default function ComparePage() {
  return (
    <Suspense fallback={<div className="section-py container-page text-muted-foreground">Загрузка…</div>}>
      <ComparePageClient />
    </Suspense>
  );
}
