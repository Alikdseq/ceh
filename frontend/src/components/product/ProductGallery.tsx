"use client";

import Image from "next/image";
import { useMemo, useState } from "react";

import { resolveStaticProductGallery, type ProductImageContext } from "@/lib/product-images";
import type { ProductImageDetail } from "@/lib/types";
import { cn, productImageSrc, productImageUnoptimized } from "@/lib/utils";

interface ProductGalleryProps {
  images: ProductImageDetail[];
  name: string;
  product?: ProductImageContext;
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

  return (
    <div className="space-y-3">
      <div className="relative aspect-square overflow-hidden rounded-lg border bg-muted">
        <Image
          src={mainSrc}
          alt={current.alt || name}
          fill
          priority
          unoptimized={productImageUnoptimized(mainSrc)}
          className="object-contain p-6"
          sizes="(max-width:768px) 100vw, 50vw"
        />
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
                <Image
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
