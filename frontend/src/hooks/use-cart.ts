"use client";

import { useCallback, useEffect, useState } from "react";

import type { CartDto } from "@/lib/api/cart-types";
import { CART_EVENT, refreshCart } from "@/lib/cart";

export function useCart(): {
  cart: CartDto | null;
  loading: boolean;
  reload: () => Promise<void>;
} {
  const [cart, setCart] = useState<CartDto | null>(null);
  const [loading, setLoading] = useState(true);

  const reload = useCallback(async () => {
    setLoading(true);
    try {
      const data = await refreshCart();
      setCart(data);
    } catch {
      setCart(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void reload();
    const onUpdate = (e: Event) => {
      const detail = (e as CustomEvent<CartDto>).detail;
      if (detail) setCart(detail);
      else void reload();
    };
    window.addEventListener(CART_EVENT, onUpdate);
    return () => window.removeEventListener(CART_EVENT, onUpdate);
  }, [reload]);

  return { cart, loading, reload };
}

export function useCartSummary(): { count: number; subtotal: string; loading: boolean } {
  const { cart, loading } = useCart();
  return {
    count: cart?.item_count ?? 0,
    subtotal: cart?.subtotal ?? "0",
    loading,
  };
}
