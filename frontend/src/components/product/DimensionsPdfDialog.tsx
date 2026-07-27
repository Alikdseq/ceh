"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { CONTACTOR_DIMENSIONS_IMAGE } from "@/lib/product-dimensions";
import { publicAssetSrc } from "@/lib/utils";

interface DimensionsPdfDialogProps {
  label?: string;
}

export function DimensionsPdfDialog({ label = "Смотреть" }: DimensionsPdfDialogProps) {
  const [open, setOpen] = useState(false);
  const [loadError, setLoadError] = useState(false);
  const imageSrc = publicAssetSrc(CONTACTOR_DIMENSIONS_IMAGE);

  return (
    <Dialog
      open={open}
      onOpenChange={(next) => {
        setOpen(next);
        if (!next) {
          setLoadError(false);
        }
      }}
    >
      <DialogTrigger asChild>
        <Button type="button" variant="outline" size="sm" className="ml-2 h-7 shrink-0 px-2 text-xs">
          {label}
        </Button>
      </DialogTrigger>
      <DialogContent className="max-h-[95vh] w-[min(96vw,920px)] max-w-[920px] gap-0 overflow-hidden p-0 sm:rounded-lg">
        <DialogHeader className="border-b px-4 py-3 pr-12">
          <DialogTitle className="text-base">Габаритные и установочные размеры</DialogTitle>
        </DialogHeader>
        <div className="max-h-[min(85vh,800px)] overflow-auto bg-white p-2">
          {loadError ? (
            <p className="px-2 py-6 text-sm text-muted-foreground">
              Не удалось загрузить схему.{" "}
              <a href={imageSrc} target="_blank" rel="noopener noreferrer" className="text-primary underline">
                Открыть изображение в новой вкладке
              </a>
            </p>
          ) : (
            // eslint-disable-next-line @next/next/no-img-element -- static PNG, no optimizer needed
            <img
              src={imageSrc}
              alt="Габаритные размеры контакторов КТ и КТП"
              className="h-auto w-full"
              onError={() => setLoadError(true)}
            />
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
