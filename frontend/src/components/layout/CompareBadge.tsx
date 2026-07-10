"use client";

import { Badge } from "@/components/ui/badge";
import { useCompareCount } from "@/hooks/use-compare-count";

export function CompareBadge() {
  const count = useCompareCount();
  if (!count) return null;
  return (
    <Badge variant="accent" className="ml-0.5 h-5 min-w-5 px-1.5 text-[10px]">
      {count}
    </Badge>
  );
}
