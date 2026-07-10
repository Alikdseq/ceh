import type { Metadata } from "next";
import { Suspense } from "react";

import { CartPageClient } from "@/components/cart/CartPageClient";

export const metadata: Metadata = {
  title: "Корзина-заявка",
  robots: { index: false, follow: true },
};

export default function CartPage() {
  return (
    <Suspense fallback={<div className="section-py container-page text-muted-foreground">Загрузка…</div>}>
      <CartPageClient />
    </Suspense>
  );
}
