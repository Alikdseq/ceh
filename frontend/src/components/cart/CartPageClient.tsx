"use client";

import Image from "next/image";
import Link from "next/link";
import { Suspense, useState } from "react";
import { FileSpreadsheet, FileText, Loader2, ShoppingCart, Trash2 } from "lucide-react";

import { QuoteForm } from "@/components/cart/QuoteForm";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { Button } from "@/components/ui/button";
import {
  clearCartApi,
  fetchCartExport,
  removeCartItem,
  updateCartItem,
} from "@/lib/api/cart";
import { dispatchCartUpdated } from "@/lib/cart";
import { catalogProductHref } from "@/lib/catalog-url";
import { useCart } from "@/hooks/use-cart";
import { cn, formatPrice, productImageSrc, productImageUnoptimized } from "@/lib/utils";
import { productImageRotateClass } from "@/lib/product-images";

export function CartPageClient() {
  const { cart, loading } = useCart();
  const [busyId, setBusyId] = useState<number | null>(null);
  const [exporting, setExporting] = useState<"pdf" | "xlsx" | null>(null);

  async function changeQty(itemId: number, quantity: number) {
    setBusyId(itemId);
    try {
      const data = await updateCartItem(itemId, quantity);
      dispatchCartUpdated(data);
    } finally {
      setBusyId(null);
    }
  }

  async function removeItem(itemId: number) {
    setBusyId(itemId);
    try {
      const data = await removeCartItem(itemId);
      dispatchCartUpdated(data);
    } finally {
      setBusyId(null);
    }
  }

  async function clearAll() {
    const data = await clearCartApi();
    dispatchCartUpdated(data);
  }

  async function handleExport(type: "pdf" | "xlsx") {
    setExporting(type);
    try {
      const blob = await fetchCartExport(type);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = type === "pdf" ? "specification.pdf" : "specification.xlsx";
      if (type === "pdf") a.target = "_blank";
      a.click();
      URL.revokeObjectURL(url);
    } finally {
      setExporting(null);
    }
  }

  const items = cart?.items ?? [];
  const isEmpty = !loading && items.length === 0;

  return (
    <div className="section-py">
      <div className="container-page">
        <Breadcrumbs
          items={[
            { label: "Главная", href: "/" },
            { label: "Корзина-заявка", href: "/cart" },
          ]}
          className="mb-6"
        />

        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h1 className="font-display text-3xl font-bold md:text-4xl">Корзина-заявка</h1>
            <p className="mt-2 text-muted-foreground">
              Сформируйте спецификацию и отправьте запрос коммерческого предложения
            </p>
          </div>
          {items.length > 0 && (
            <div className="flex flex-wrap gap-2">
              <Button
                variant="outline"
                size="sm"
                className="gap-1"
                disabled={!!exporting}
                onClick={() => void handleExport("pdf")}
              >
                {exporting === "pdf" ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <FileText className="h-4 w-4" />
                )}
                PDF
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="gap-1"
                disabled={!!exporting}
                onClick={() => void handleExport("xlsx")}
              >
                {exporting === "xlsx" ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <FileSpreadsheet className="h-4 w-4" />
                )}
                Excel
              </Button>
              <Button variant="outline" size="sm" onClick={() => void clearAll()}>
                Очистить
              </Button>
            </div>
          )}
        </div>

        {loading && (
          <div className="mt-16 flex justify-center text-muted-foreground">
            <Loader2 className="h-8 w-8 animate-spin" aria-label="Загрузка" />
          </div>
        )}

        {isEmpty && (
          <div className="mt-12 rounded-lg border bg-muted/30 p-10 text-center">
            <ShoppingCart className="mx-auto h-12 w-12 text-muted-foreground/50" />
            <p className="mt-4 text-lg text-muted-foreground">Корзина пуста</p>
            <Button asChild className="mt-6">
              <Link href="/catalog/">Перейти в каталог</Link>
            </Button>
          </div>
        )}

        {items.length > 0 && (
          <div className="mt-8 grid gap-10 lg:grid-cols-[1fr_380px]">
            <div className="overflow-x-auto rounded-lg border">
              <table className="w-full min-w-[720px] text-sm">
                <thead className="border-b bg-muted/40">
                  <tr>
                    <th className="px-4 py-3 text-left font-medium">Товар</th>
                    <th className="px-4 py-3 text-left font-medium whitespace-nowrap">Без НДС</th>
                    <th className="px-4 py-3 text-left font-medium whitespace-nowrap">С НДС</th>
                    <th className="px-4 py-3 text-left font-medium">Кол-во</th>
                    <th className="px-4 py-3 text-left font-medium whitespace-nowrap">Сумма с НДС</th>
                    <th className="px-4 py-3" />
                  </tr>
                </thead>
                <tbody>
                  {items.map((item) => {
                    const href = catalogProductHref(item);
                    const busy = busyId === item.id;
                    const imageContext = {
                      name: item.product_name,
                      sku_code: item.sku_code,
                    };
                    const imageSrc = productImageSrc(item.image_url, imageContext);
                    const rotateClass = productImageRotateClass(imageContext);
                    return (
                      <tr key={item.id} className="border-b">
                        <td className="px-4 py-3">
                          <div className="flex gap-3">
                            <div className="relative h-16 w-16 shrink-0 overflow-hidden rounded bg-muted">
                              <Image
                                src={imageSrc}
                                alt={item.product_name}
                                fill
                                unoptimized={productImageUnoptimized(imageSrc)}
                                className={cn("object-contain p-1", rotateClass)}
                                sizes="64px"
                              />
                            </div>
                            <div>
                              <Link href={href} className="font-medium hover:text-primary">
                                {item.product_name}
                              </Link>
                              <p className="text-xs text-muted-foreground">{item.sku_code}</p>
                            </div>
                          </div>
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-muted-foreground">
                          {formatPrice(item.unit_price_without_vat ?? item.unit_price)}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap">{formatPrice(item.unit_price)}</td>
                        <td className="px-4 py-3">
                          <div className="flex items-center rounded-md border w-fit">
                            <Button
                              type="button"
                              variant="ghost"
                              size="icon"
                              className="h-8 w-8"
                              disabled={busy}
                              onClick={() => void changeQty(item.id, Math.max(0, item.quantity - 1))}
                            >
                              −
                            </Button>
                            <span className="w-10 text-center">{item.quantity}</span>
                            <Button
                              type="button"
                              variant="ghost"
                              size="icon"
                              className="h-8 w-8"
                              disabled={busy}
                              onClick={() => void changeQty(item.id, Math.min(9999, item.quantity + 1))}
                            >
                              +
                            </Button>
                          </div>
                        </td>
                        <td className="px-4 py-3 font-medium whitespace-nowrap">
                          {formatPrice(item.line_total)}
                        </td>
                        <td className="px-4 py-3">
                          <Button
                            type="button"
                            variant="ghost"
                            size="icon"
                            disabled={busy}
                            aria-label="Удалить"
                            onClick={() => void removeItem(item.id)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            <aside className="space-y-6">
              <div className="rounded-lg border bg-card p-5">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Позиций</span>
                  <span>{cart?.item_count}</span>
                </div>
                <div className="mt-2 flex justify-between text-sm">
                  <span className="text-muted-foreground">Итого без НДС</span>
                  <span>{formatPrice(cart?.subtotal_without_vat ?? cart?.subtotal ?? "0")}</span>
                </div>
                <div className="mt-2 flex justify-between text-lg font-semibold">
                  <span>Итого с НДС</span>
                  <span className="font-semibold text-foreground">{formatPrice(cart?.subtotal ?? "0")}</span>
                </div>
                <p className="mt-1 text-xs text-muted-foreground">Цены указаны с НДС 22%</p>
              </div>

              <div className="rounded-lg border bg-card p-5">
                <h2 className="font-display text-lg font-semibold">Оформление заявки</h2>
                <div className="mt-4">
                  <Suspense fallback={<p className="text-sm text-muted-foreground">Загрузка формы…</p>}>
                    <QuoteForm />
                  </Suspense>
                </div>
              </div>
            </aside>
          </div>
        )}
      </div>
    </div>
  );
}
