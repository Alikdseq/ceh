"use client";

import { useMemo, useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { ShoppingCart } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { HonestSignMark } from "@/components/content/HonestSignMark";
import { addToCart } from "@/lib/cart";
import { showHonestSignMarking } from "@/lib/honest-sign";
import { highlightMatch } from "@/lib/search-highlight";
import type { ProductGroup } from "@/lib/types";
import { listAuxContacts, pickProductVariant } from "@/lib/variant-picker";
import { productImageRotateClass } from "@/lib/product-images";
import { sortCoilVoltages } from "@/lib/coil-voltages";
import {
  cn,
  formatAuxContactsLabel,
  formatPrice,
  productImageSrc,
  productImageUnoptimized,
  PRODUCT_IMAGE_ASPECT_CLASS,
} from "@/lib/utils";

interface ProductCardProps {
  product: ProductGroup;
  categoryPath: string[];
  view?: "grid" | "list";
  highlightQuery?: string;
  priority?: boolean;
}

export function ProductCard({
  product,
  categoryPath,
  view = "grid",
  highlightQuery,
  priority = false,
}: ProductCardProps) {
  const href = `/catalog/${[...categoryPath, product.slug].join("/")}`;
  const variants = product.variants_preview ?? (product.default_variant ? [product.default_variant] : []);

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
    product.default_variant?.coil_voltage_v ?? coils[0] ?? null,
  );
  const [auxContacts, setAuxContacts] = useState<string | null>(
    product.default_variant?.aux_contacts ?? auxOptions[0] ?? null,
  );

  const selected =
    pickProductVariant(variants, null, coil, auxContacts) ??
    product.default_variant ??
    variants[0];

  const imageSrc = productImageSrc(product.primary_image?.url, product);
  const hasHonestSign = showHonestSignMarking(product);
  const imageContext = {
    name: product.name,
    slug: product.slug,
    series_code: product.series_code,
    product_type: product.product_type,
    sku_code: selected?.sku_code ?? product.default_variant?.sku_code,
    execution: selected?.execution ?? product.default_variant?.execution,
    coil_voltage_v: selected?.coil_voltage_v ?? product.default_variant?.coil_voltage_v,
  };
  const rotateClass = productImageRotateClass(imageContext);

  function syncSelection(nextCoil: number | null, nextAux: string | null) {
    const matched = pickProductVariant(variants, null, nextCoil, nextAux);
    if (matched?.coil_voltage_v != null) setCoil(matched.coil_voltage_v);
    if (matched?.aux_contacts) setAuxContacts(matched.aux_contacts);
  }

  function selectCoil(voltage: number) {
    setCoil(voltage);
    syncSelection(voltage, auxContacts);
  }

  function selectAuxContacts(value: string) {
    setAuxContacts(value);
    syncSelection(coil, value);
  }

  function handleAddToCart() {
    const variant = pickProductVariant(variants, null, coil, auxContacts) ?? selected;
    if (!variant) return;
    void addToCart({
      variantId: variant.id,
      skuCode: variant.sku_code,
      name: product.name,
      price: variant.price,
    });
  }

  const imageBlock = (
    <Link
      href={href}
      className={cn(
        "relative block shrink-0 overflow-hidden bg-muted transition hover:opacity-95",
        view === "grid"
          ? `${PRODUCT_IMAGE_ASPECT_CLASS} w-full`
          : `h-24 w-40 shrink-0 rounded-md ${PRODUCT_IMAGE_ASPECT_CLASS}`,
      )}
    >
      <Image
        src={imageSrc}
        alt={product.primary_image?.alt ?? product.name}
        fill
        priority={priority}
        loading={priority ? "eager" : "lazy"}
        unoptimized={productImageUnoptimized(imageSrc)}
        className={cn("object-contain p-3", rotateClass)}
        sizes={view === "grid" ? "(max-width:640px) 100vw, 33vw" : "112px"}
      />
      <Badge variant="brand" className="absolute left-2 top-2 text-[10px]">
        Производитель
      </Badge>
      {hasHonestSign && (
        <HonestSignMark size="sm" className="absolute bottom-2 right-2 rounded bg-white/90 p-0.5" />
      )}
    </Link>
  );

  const variantSwitcher =
    coils.length > 0 || auxOptions.length > 0 ? (
      <div className="mt-2 space-y-2" onClick={(e) => e.stopPropagation()}>
        {coils.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {coils.map((v) => (
              <Button
                key={v}
                type="button"
                size="sm"
                variant={coil === v ? "default" : "outline"}
                className="h-7 px-2 text-xs"
                onClick={() => selectCoil(v)}
              >
                {v} В
              </Button>
            ))}
          </div>
        )}
        {auxOptions.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {auxOptions.map((value) => (
              <Button
                key={value}
                type="button"
                size="sm"
                variant={auxContacts === value ? "default" : "outline"}
                className="h-7 px-2 text-xs"
                onClick={() => selectAuxContacts(value)}
              >
                {formatAuxContactsLabel(value)}
              </Button>
            ))}
          </div>
        )}
        {selected?.sku_code && (
          <p className="text-xs text-muted-foreground">
            Артикул: <span className="font-mono">{selected.sku_code}</span>
          </p>
        )}
      </div>
    ) : null;

  const titleBlock = (
    <div className="min-w-0 flex-1">
      <Link href={href} className="block">
        <h3 className="font-display font-semibold leading-snug hover:text-primary">
          {highlightQuery ? highlightMatch(product.name, highlightQuery) : product.name}
        </h3>
        {product.series_code && highlightQuery && (
          <p className="mt-0.5 text-xs text-muted-foreground">
            {highlightMatch(product.series_code, highlightQuery)}
            {selected?.sku_code && <> · {highlightMatch(selected.sku_code, highlightQuery)}</>}
          </p>
        )}
        {product.nominal_current_a && (
          <p className="mt-1 text-sm text-muted-foreground">{product.nominal_current_a} А</p>
        )}
        <p className="mt-2 text-lg font-semibold text-foreground">
          от {formatPrice(selected?.price ?? product.price_from)}
          <span className="ml-1 text-xs font-normal text-muted-foreground">с НДС</span>
        </p>
      </Link>
      {variantSwitcher}
    </div>
  );

  const actions = (
    <div
      className={cn(
        "flex gap-2",
        view === "grid" ? "mt-4 flex-col sm:flex-row" : "shrink-0 flex-col justify-center",
      )}
    >
      <Button asChild variant="outline" size="sm" className="flex-1">
        <Link href={href}>Подробнее</Link>
      </Button>
      <Button
        size="sm"
        variant="accent"
        className="flex-1 gap-1"
        disabled={!selected}
        onClick={handleAddToCart}
      >
        <ShoppingCart className="h-3.5 w-3.5" />
        В заявку
      </Button>
    </div>
  );

  return (
    <article
      className={cn(
        "rounded-lg border bg-card transition hover:border-primary hover:shadow-md",
        view === "grid" ? "overflow-hidden" : "flex gap-4 p-4",
      )}
    >
      {view === "grid" ? (
        <>
          {imageBlock}
          <div className="p-4">
            {titleBlock}
            {actions}
          </div>
        </>
      ) : (
        <>
          {imageBlock}
          <div className="flex min-w-0 flex-1 flex-col justify-center">
            {titleBlock}
            {actions}
          </div>
        </>
      )}
    </article>
  );
}
