"use client";

import { Badge } from "@/components/ui/badge";
import { useCartSummary } from "@/hooks/use-cart";

export function CartBadge() {
  const { count } = useCartSummary();
  return (
    <Badge variant="accent" className="ml-0.5 h-5 min-w-5 px-1.5 text-[10px]">
      {count}
    </Badge>
  );
}
