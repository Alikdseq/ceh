"use client";

import { useMemo, useState } from "react";

import { ProductImageFit } from "@/components/product/ProductImageFit";

import { resolveStaticProductGallery, type ProductImageContext } from "@/lib/product-images";
import type { ProductImageDetail } from "@/lib/types";
import { showHonestSignMarking } from "@/lib/honest-sign";
import { cn, productImageSrc, productImageUnoptimized, PRODUCT_IMAGE_ASPECT_CLASS } from "@/lib/utils";
import { HonestSignMark } from "@/components/content/HonestSignMark";

interface ProductGalleryProps {
  images: ProductImageDetail[];
  name: string;
  product?: ProductImageContext & { honest_sign?: boolean; product_type?: string };
}

function galleryItemSrc(item: ProductImageDetail | { url?: string; image?: string }): string {
  return item.url ?? ("image" in item ? item.image : undefined) ?? "";
}

export function ProductGallery({ images, name, product }: ProductGalleryProps) {
  const list = useMemo(() => {
    const staticUrls = product ? resolveStaticProductGallery(product) : [];
    if (staticUrls.length > 0) {
      return staticUrls.map((url, index) => ({
        id: index,
        url,
        alt: name,
        sort_order: index,
        is_primary: index === 0,
      }));
    }

    const sorted = [...images].sort((a, b) => Number(b.is_primary) - Number(a.is_primary));
    if (sorted.length > 0) return sorted;

    return [{ id: 0, alt: name, sort_order: 0, is_primary: true, url: "/placeholder-product.svg" }];
  }, [images, name, product]);

  const [active, setActive] = useState(0);
  const current = list[active] ?? list[0];
  const mainSrc = productImageSrc(galleryItemSrc(current), product);
  const hasHonestSign = product ? showHonestSignMarking(product) : false;

  return (
    <div className="space-y-3">
      <div className={cn("relative overflow-hidden rounded-lg border bg-muted", PRODUCT_IMAGE_ASPECT_CLASS)}>
        <ProductImageFit
          src={mainSrc}
          alt={current.alt || name}
          fill
          priority
          unoptimized={productImageUnoptimized(mainSrc)}
          className="object-contain p-6"
          sizes="(max-width:768px) 100vw, 50vw"
        />
        {hasHonestSign && (
          <HonestSignMark size="md" className="absolute bottom-3 right-3 rounded-md bg-white/95 p-1 shadow-sm" />
        )}
      </div>
      {list.length > 1 && (
        <div className="flex gap-2 overflow-x-auto pb-1">
          {list.map((img, idx) => {
            const thumbSrc = productImageSrc(galleryItemSrc(img), product);
            return (
              <button
                key={img.id}
                type="button"
                onClick={() => setActive(idx)}
                className={cn(
                  "relative h-16 w-16 shrink-0 overflow-hidden rounded-md border bg-muted",
                  idx === active && "ring-2 ring-primary",
                )}
              >
                <ProductImageFit
                  src={thumbSrc}
                  alt=""
                  fill
                  unoptimized={productImageUnoptimized(thumbSrc)}
                  className="object-contain p-1"
                  sizes="64px"
                />
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
