"use client";

import Image from "next/image";
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

interface DimensionsPdfDialogProps {
  label?: string;
}

export function DimensionsPdfDialog({ label = "Смотреть" }: DimensionsPdfDialogProps) {
  const [open, setOpen] = useState(false);

  return (
    <Dialog open={open} onOpenChange={setOpen}>
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
          <Image
            src={CONTACTOR_DIMENSIONS_IMAGE}
            alt="Габаритные размеры контакторов КТ и КТП"
            width={900}
            height={1200}
            className="h-auto w-full"
            unoptimized
          />
        </div>
      </DialogContent>
    </Dialog>
  );
}
