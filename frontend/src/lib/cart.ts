"use client";

import { addCartItem as addCartItemApi, fetchCart } from "@/lib/api/cart";
import type { CartDto } from "@/lib/api/cart-types";

export type { CartDto, CartItemDto } from "@/lib/api/cart-types";

const CART_EVENT = "cart-updated";

export function dispatchCartUpdated(cart?: CartDto): void {
  window.dispatchEvent(new CustomEvent(CART_EVENT, { detail: cart }));
}

export async function refreshCart(): Promise<CartDto> {
  const cart = await fetchCart();
  dispatchCartUpdated(cart);
  return cart;
}

export async function addToCart(
  item: { variantId: number; skuCode?: string; name?: string; price?: string },
  quantity = 1,
): Promise<CartDto> {
  const cart = await addCartItemApi(item.variantId, quantity);
  dispatchCartUpdated(cart);
  return cart;
}

export function getCartCountFrom(cart: CartDto | null): number {
  return cart?.item_count ?? 0;
}

export function getCartSubtotalFrom(cart: CartDto | null): string {
  return cart?.subtotal ?? "0";
}

export { CART_EVENT };
