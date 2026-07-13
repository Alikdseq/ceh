"use client";

import Image, { type ImageProps } from "next/image";
import { useState } from "react";

import { cn } from "@/lib/utils";

/** Rotate portrait product photos to fit horizontal card frames. */
export function ProductImageFit({ className, onLoad, ...props }: ImageProps) {
  const [portrait, setPortrait] = useState(false);

  return (
    <Image
      {...props}
      onLoad={(event) => {
        const img = event.currentTarget;
        if (img.naturalHeight > img.naturalWidth * 1.08) {
          setPortrait(true);
        }
        onLoad?.(event);
      }}
      className={cn(
        className,
        portrait && "rotate-90 scale-[1.42] object-contain",
      )}
    />
  );
}
