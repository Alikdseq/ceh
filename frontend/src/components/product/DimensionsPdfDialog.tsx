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
import { CONTACTOR_DIMENSIONS_PDF } from "@/lib/product-dimensions";

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
      <DialogContent className="max-h-[95vh] w-[min(96vw,900px)] max-w-[900px] gap-0 overflow-hidden p-0 sm:rounded-lg">
        <DialogHeader className="border-b px-4 py-3 pr-12">
          <DialogTitle className="text-base">Габаритные и установочные размеры</DialogTitle>
        </DialogHeader>
        <iframe
          title="Габаритные размеры контакторов КТ 6013–6053"
          src={CONTACTOR_DIMENSIONS_PDF}
          className="h-[min(80vh,720px)] w-full border-0 bg-muted"
        />
      </DialogContent>
    </Dialog>
  );
}
