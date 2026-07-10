"use client";

import { GitCompare } from "lucide-react";

import { Button } from "@/components/ui/button";
import { addToCompare, getCompareCount, MAX_COMPARE } from "@/lib/compare";
import { cn } from "@/lib/utils";

interface CompareButtonProps {
  variantId: number | undefined;
  className?: string;
  size?: "sm" | "default" | "lg" | "icon";
  showLabel?: boolean;
}

export function CompareButton({
  variantId,
  className,
  size = "sm",
  showLabel = true,
}: CompareButtonProps) {
  function handleClick() {
    if (!variantId) return;
    const added = addToCompare(variantId);
    if (!added) {
      window.alert(`Можно сравнить не более ${MAX_COMPARE} позиций. Удалите товар на странице сравнения.`);
    }
  }

  return (
    <Button
      type="button"
      variant="outline"
      size={size}
      className={cn("gap-1", className)}
      disabled={!variantId}
      onClick={handleClick}
      aria-label={
        showLabel
          ? undefined
          : `Добавить в сравнение (${getCompareCount()}/${MAX_COMPARE})`
      }
    >
      <GitCompare className="h-4 w-4" />
      {showLabel && "Сравнить"}
    </Button>
  );
}
