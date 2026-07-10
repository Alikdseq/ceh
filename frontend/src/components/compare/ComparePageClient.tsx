"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { Loader2, ShoppingCart, Trash2, X } from "lucide-react";

import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { Button } from "@/components/ui/button";
import { fetchApiClient } from "@/lib/api/client";
import { addToCart } from "@/lib/cart";
import {
  clearCompare,
  getCompareIds,
  removeFromCompare,
  setCompareIds,
} from "@/lib/compare";
import { cn, coilTypeLabel, executionLabel, formatPrice, productTypeLabel, specKeyLabel } from "@/lib/utils";
import type { CompareResponse, CompareVariant } from "@/lib/types";

const BASE_ROWS: { key: string; label: string; get: (v: CompareVariant) => string }[] = [
  { key: "sku", label: "Артикул", get: (v) => v.sku_code },
  { key: "price", label: "Цена", get: (v) => formatPrice(v.price) },
  { key: "execution", label: "Исполнение", get: (v) => executionLabel(v.execution) },
  {
    key: "coil",
    label: "Катушка",
    get: (v) =>
      v.coil_voltage_v ? `${v.coil_voltage_v} В` : v.coil_type ? coilTypeLabel(v.coil_type) : "—",
  },
  { key: "current", label: "Номинальный ток, А", get: (v) => (v.nominal_current_a ? String(v.nominal_current_a) : "—") },
  { key: "poles", label: "Число полюсов", get: (v) => (v.poles ? String(v.poles) : "—") },
  { key: "type", label: "Тип", get: (v) => productTypeLabel(v.product_type) },
];

function parseUrlIds(raw: string | null): number[] {
  if (!raw) return [];
  return raw
    .split(",")
    .map((x) => parseInt(x.trim(), 10))
    .filter((id) => !Number.isNaN(id));
}

function valuesDiffer(values: string[]): boolean {
  if (values.length <= 1) return false;
  return new Set(values).size > 1;
}

export function ComparePageClient() {
  const searchParams = useSearchParams();
  const [ids, setIds] = useState<number[]>([]);
  const [data, setData] = useState<CompareResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadCompare = useCallback(async (variantIds: number[]) => {
    if (!variantIds.length) {
      setData(null);
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const response = await fetchApiClient<CompareResponse>("/compare/", {
        params: new URLSearchParams({ ids: variantIds.join(",") }),
      });
      setData(response);
    } catch {
      setError("Не удалось загрузить данные для сравнения.");
      setData(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const urlIds = parseUrlIds(searchParams.get("ids"));
    const stored = getCompareIds();
    const merged = urlIds.length
      ? [...new Set([...urlIds, ...stored])].slice(0, 4)
      : stored;
    if (merged.length && JSON.stringify(merged) !== JSON.stringify(stored)) {
      setCompareIds(merged);
    }
    setIds(merged);
    void loadCompare(merged);
  }, [searchParams, loadCompare]);

  useEffect(() => {
    function onCompareUpdate() {
      const next = getCompareIds();
      setIds(next);
      void loadCompare(next);
    }
    window.addEventListener("compare-updated", onCompareUpdate);
    return () => window.removeEventListener("compare-updated", onCompareUpdate);
  }, [loadCompare]);

  function handleRemove(variantId: number) {
    removeFromCompare(variantId);
  }

  function handleAddAllToCart() {
    if (!data?.variants.length) return;
    data.variants.forEach((v) => {
      void addToCart({
        variantId: v.id,
        skuCode: v.sku_code,
        name: v.group_name,
        price: v.price,
      });
    });
  }

  const baseSpecKeys = new Set([
    ...BASE_ROWS.map((r) => r.key),
    "nominal_current",
    "nominal_voltage",
    "poles",
    "execution",
    "product_type",
    "coil_type",
    "coil_voltage_ac",
    "coil_voltage_dc",
  ]);

  const specRows =
    data?.spec_keys
      .filter((key) => !baseSpecKeys.has(key))
      .map((key) => ({
        key: `spec:${key}`,
        label: specKeyLabel(key),
        get: (v: CompareVariant) => v.specs.find((s) => s.spec_key === key)?.spec_value ?? "—",
      })) ?? [];

  const allRows = [...BASE_ROWS, ...specRows];

  return (
    <div className="section-py">
      <div className="container-page">
        <Breadcrumbs
          items={[
            { label: "Главная", href: "/" },
            { label: "Сравнение", href: "/compare" },
          ]}
          className="mb-6"
        />

        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h1 className="font-display text-3xl font-bold md:text-4xl">Сравнение товаров</h1>
            <p className="mt-2 text-muted-foreground">До 4 позиций одновременно</p>
          </div>
          {ids.length > 0 && (
            <div className="flex flex-wrap gap-2">
              <Button variant="accent" className="gap-2" onClick={handleAddAllToCart} disabled={!data?.variants.length}>
                <ShoppingCart className="h-4 w-4" />
                Добавить все в заявку
              </Button>
              <Button variant="outline" onClick={() => clearCompare()}>
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

        {!loading && !ids.length && (
          <div className="mt-12 rounded-lg border bg-muted/30 p-8 text-center">
            <p className="text-lg text-muted-foreground">Список сравнения пуст.</p>
            <Button asChild className="mt-4">
              <Link href="/catalog/">Перейти в каталог</Link>
            </Button>
          </div>
        )}

        {error && !loading && (
          <p className="mt-8 text-destructive">{error}</p>
        )}

        {!loading && data && data.variants.length > 0 && (
          <div className="mt-8 overflow-x-auto rounded-lg border">
            <table className="w-full min-w-[640px] border-collapse text-sm">
              <thead>
                <tr className="border-b bg-muted/40">
                  <th className="sticky left-0 z-10 min-w-[140px] bg-muted/40 px-4 py-3 text-left font-medium">
                    Характеристика
                  </th>
                  {data.variants.map((v) => (
                    <th key={v.id} className="min-w-[180px] px-4 py-3 text-left align-top">
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <Link
                            href={`/catalog/${v.group_slug}`}
                            className="font-display font-semibold hover:text-primary"
                          >
                            {v.group_name}
                          </Link>
                          <p className="mt-1 text-xs text-muted-foreground">{v.sku_code}</p>
                        </div>
                        <Button
                          type="button"
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8 shrink-0 text-muted-foreground"
                          aria-label="Удалить из сравнения"
                          onClick={() => handleRemove(v.id)}
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      </div>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {allRows.map((row) => {
                  const values = data.variants.map((v) => row.get(v));
                  const diff = valuesDiffer(values);
                  return (
                    <tr key={row.key} className={cn("border-b", diff && "bg-accent/5")}>
                      <td className="sticky left-0 z-10 bg-background px-4 py-3 font-medium text-muted-foreground">
                        {row.label}
                      </td>
                      {data.variants.map((v, i) => (
                        <td
                          key={v.id}
                          className={cn(
                            "px-4 py-3",
                            diff && "font-medium text-foreground",
                          )}
                        >
                          {values[i]}
                        </td>
                      ))}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        {!loading && ids.length > 0 && data && data.variants.length < ids.length && (
          <p className="mt-4 flex items-center gap-2 text-sm text-muted-foreground">
            <Trash2 className="h-4 w-4" />
            Некоторые позиции недоступны и были скрыты.
          </p>
        )}
      </div>
    </div>
  );
}
