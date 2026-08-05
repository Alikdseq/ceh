"use client";

import Image from "next/image";
import { useState } from "react";
import { ZoomIn } from "lucide-react";

import {
  Dialog,
  DialogContent,
  DialogTitle,
} from "@/components/ui/dialog";
import { normalizeMediaUrl } from "@/lib/utils";

interface NewsPostImageViewerProps {
  src: string;
  alt: string;
}

export function NewsPostImageViewer({ src, alt }: NewsPostImageViewerProps) {
  const [open, setOpen] = useState(false);
  const imageSrc = normalizeMediaUrl(src);

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="group relative mt-6 block w-full overflow-hidden rounded-lg border bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
        aria-label={`Открыть фото: ${alt}`}
      >
        <div className="relative aspect-[16/10] w-full">
          <Image
            src={imageSrc}
            alt={alt}
            fill
            unoptimized
            className="object-contain p-2 transition duration-200 group-hover:scale-[1.01]"
            sizes="(max-width:768px) 100vw, 768px"
          />
        </div>
        <span className="absolute bottom-3 right-3 inline-flex items-center gap-1 rounded-md bg-black/65 px-2.5 py-1 text-xs text-white">
          <ZoomIn className="h-3.5 w-3.5" aria-hidden />
          Увеличить
        </span>
      </button>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="max-h-[95vh] w-[min(96vw,960px)] max-w-[960px] gap-0 overflow-hidden border-0 bg-black/95 p-2 sm:rounded-lg">
          <DialogTitle className="sr-only">{alt}</DialogTitle>
          {/* eslint-disable-next-line @next/next/no-img-element -- full-size media preview */}
          <img
            src={imageSrc}
            alt={alt}
            className="mx-auto max-h-[min(88vh,900px)] w-auto max-w-full object-contain"
          />
        </DialogContent>
      </Dialog>
    </>
  );
}
