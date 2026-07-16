"use client";

import { useCallback, useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { ShoppingCart } from "lucide-react";
import { CompareButton } from "@/components/product/CompareButton";
import { HonestSignMark } from "@/components/content/HonestSignMark";

import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { addToCart } from "@/lib/cart";
import { showHonestSignMarking } from "@/lib/honest-sign";
import type { ProductGroupDetail, ProductVariant } from "@/lib/types";
import { listAuxContacts, pickProductVariant } from "@/lib/variant-picker";
import { sortCoilVoltages } from "@/lib/coil-voltages";
import { formatAuxContactsLabel, formatPrice } from "@/lib/utils";

interface ProductConfiguratorProps {
  product: ProductGroupDetail;
  basePath: string;
}

export function ProductConfigurator({ product, basePath }: ProductConfiguratorProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const variants = product.variants;

  const variantFromUrl = variants.find((v) => v.slug === searchParams.get("variant"));

  const coils = useMemo(
    () =>
      sortCoilVoltages(
        variants.map((v) => v.coil_voltage_v).filter((v): v is number => v != null),
      ),
    [variants],
  );
  const auxOptions = useMemo(() => {
    if (product.aux_contacts_options?.length) return product.aux_contacts_options;
    return listAuxContacts(variants);
  }, [product.aux_contacts_options, variants]);

  const [coil, setCoil] = useState<number | null>(
    variantFromUrl?.coil_voltage_v ?? coils[0] ?? null,
  );
  const [auxContacts, setAuxContacts] = useState<string | null>(
    variantFromUrl?.aux_contacts ?? auxOptions[0] ?? null,
  );
  const [quantity, setQuantity] = useState(1);

  const selected =
    variantFromUrl ??
    pickProductVariant(variants, null, coil, auxContacts) ??
    variants.find((v) => v.is_default) ??
    variants[0];

  const updateUrl = useCallback(
    (variant: ProductVariant) => {
      const sp = new URLSearchParams(searchParams.toString());
      sp.set("variant", variant.slug);
      router.replace(`${basePath}?${sp.toString()}`, { scroll: false });
    },
    [basePath, router, searchParams],
  );

  function applySelection(nextCoil: number | null, nextAux: string | null) {
    const variant = pickProductVariant(variants, null, nextCoil, nextAux);
    if (variant) updateUrl(variant);
  }

  function selectCoil(voltage: string) {
    const vNum = Number(voltage);
    setCoil(vNum);
    applySelection(vNum, auxContacts);
  }

  function selectAuxContacts(value: string) {
    setAuxContacts(value);
    applySelection(coil, value);
  }

  function handleAddToCart() {
    if (!selected) return;
    void addToCart(
      {
        variantId: selected.id,
        skuCode: selected.sku_code,
        name: product.name,
        price: selected.price,
      },
      quantity,
    );
  }

  const passport = product.documents.find(
    (d) =>
      d.document.doc_type?.toLowerCase().includes("passport") ||
      d.document.name.toLowerCase().includes("паспорт"),
  );

  return (
    <div className="min-w-0 space-y-6">
      <div>
        <div className="flex flex-wrap items-start gap-2">
          <h1 className="font-display text-2xl font-bold break-words md:text-3xl">{product.h1 || product.name}</h1>
          {showHonestSignMarking(product) && (
            <HonestSignMark size="md" className="mt-1 rounded-md bg-[#FAFF00]/25 p-1" />
          )}
        </div>
        {product.nominal_current_a && (
          <p className="mt-2 text-muted-foreground">Номинальный ток: {product.nominal_current_a} А</p>
        )}
      </div>

      {coils.length > 0 && (
        <div className="space-y-2">
          <Label>Напряжение катушки</Label>
          <div className="flex flex-wrap gap-2">
            {coils.map((v) => (
              <Button
                key={v}
                type="button"
                size="sm"
                variant={coil === v ? "default" : "outline"}
                onClick={() => selectCoil(String(v))}
              >
                {v} В
              </Button>
            ))}
          </div>
        </div>
      )}

      {auxOptions.length > 0 && (
        <div className="space-y-2">
          <Label>Количество вспомогательных контактов</Label>
          <div className="flex flex-wrap gap-2">
            {auxOptions.map((value) => (
              <Button
                key={value}
                type="button"
                size="sm"
                variant={auxContacts === value ? "default" : "outline"}
                onClick={() => selectAuxContacts(value)}
              >
                {formatAuxContactsLabel(value)}
              </Button>
            ))}
          </div>
        </div>
      )}

      {selected && (
        <div className="rounded-lg border border-border bg-[var(--color-brand-blue-light)] p-4 text-sm">
          <p>
            <span className="text-muted-foreground">Артикул:</span>{" "}
            <span className="font-mono font-medium text-primary">{selected.sku_code}</span>
          </p>
          {selected.aux_contacts && (
            <p className="mt-1">
              <span className="text-muted-foreground">Всп. контакты:</span> {formatAuxContactsLabel(selected.aux_contacts)}
            </p>
          )}
        </div>
      )}

      <div className="flex items-baseline gap-2">
        <span className="font-display text-3xl font-bold text-foreground">
          {formatPrice(selected?.price)}
        </span>
        {selected && parseFloat(selected.price) > 0 && (
          <span className="text-sm text-muted-foreground">с НДС</span>
        )}
        {selected && parseFloat(selected.price) <= 0 && (
          <span className="text-sm text-muted-foreground">уточняйте у менеджера</span>
        )}
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <Label htmlFor="qty" className="sr-only">
          Количество
        </Label>
        <div className="flex shrink-0 items-center rounded-md border">
          <Button
            type="button"
            variant="ghost"
            size="icon"
            className="h-10 w-10"
            onClick={() => setQuantity((q) => Math.max(1, q - 1))}
            aria-label="Уменьшить"
          >
            −
          </Button>
          <input
            id="qty"
            type="number"
            min={1}
            max={9999}
            value={quantity}
            onChange={(e) =>
              setQuantity(Math.min(9999, Math.max(1, Number(e.target.value) || 1)))
            }
            className="w-16 border-x bg-transparent text-center text-sm outline-none"
          />
          <Button
            type="button"
            variant="ghost"
            size="icon"
            className="h-10 w-10"
            onClick={() => setQuantity((q) => Math.min(9999, q + 1))}
            aria-label="Увеличить"
          >
            +
          </Button>
        </div>
        <Button
          size="lg"
          variant="accent"
          className="min-w-0 flex-1 basis-full gap-2 sm:basis-auto"
          onClick={handleAddToCart}
          disabled={!selected}
        >
          <ShoppingCart className="h-4 w-4" />
          Добавить в заявку
        </Button>
      </div>

      <div className="flex flex-wrap gap-2">
        <CompareButton variantId={selected?.id} />
        <Button asChild variant="outline" size="sm">
          <Link href="/compare">К сравнению</Link>
        </Button>
        {passport?.document.file_url && (
          <Button asChild variant="outline" size="sm">
            <a href={passport.document.file_url} target="_blank" rel="noopener noreferrer">
              Скачать паспорт
            </a>
          </Button>
        )}
      </div>
    </div>
  );
}

export function ProductStickyBar({
  product,
  selected,
}: {
  product: ProductGroupDetail;
  selected: ProductVariant | undefined;
}) {
  if (!selected) return null;

  function handleAdd() {
    void addToCart(
      {
        variantId: selected!.id,
        skuCode: selected!.sku_code,
        name: product.name,
        price: selected!.price,
      },
      1,
    );
  }

  return (
    <div className="fixed inset-x-0 bottom-0 z-40 border-t bg-background/95 p-3 shadow-lg backdrop-blur md:hidden">
      <div className="container-page flex items-center gap-3">
        <div className="min-w-0 flex-1">
          <p className="truncate text-sm font-medium">{product.name}</p>
          <p className="font-semibold text-foreground">{formatPrice(selected.price)}</p>
        </div>
        <Button size="sm" variant="accent" className="shrink-0 gap-1" onClick={handleAdd}>
          <ShoppingCart className="h-4 w-4" />
          В заявку
        </Button>
      </div>
    </div>
  );
}
