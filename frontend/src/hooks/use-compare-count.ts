"use client";

import { useEffect, useState } from "react";

import { COMPARE_EVENT, getCompareCount } from "@/lib/compare";

export function useCompareCount(): number {
  const [count, setCount] = useState(0);

  useEffect(() => {
    const update = () => setCount(getCompareCount());
    update();
    window.addEventListener(COMPARE_EVENT, update);
    window.addEventListener("storage", update);
    return () => {
      window.removeEventListener(COMPARE_EVENT, update);
      window.removeEventListener("storage", update);
    };
  }, []);

  return count;
}
