import { fetchCartApi, getApiBase } from "@/lib/api/client";
import { cartSessionHeaders, syncCartSessionFromResponse } from "@/lib/cart-session";

import type { CartDto } from "./cart-types";

export type { CartDto, CartItemDto, QuoteSubmitPayload, QuoteSubmitResponse } from "./cart-types";

export async function fetchCart(): Promise<CartDto> {
  const { data } = await fetchCartApi<CartDto>("/cart/");
  return data;
}

export async function addCartItem(variantId: number, quantity = 1): Promise<CartDto> {
  const { data } = await fetchCartApi<CartDto>("/cart/items/", {
    method: "POST",
    body: JSON.stringify({ variant_id: variantId, quantity }),
  });
  return data;
}

export async function updateCartItem(itemId: number, quantity: number): Promise<CartDto> {
  const { data } = await fetchCartApi<CartDto>(`/cart/items/${itemId}/`, {
    method: "PATCH",
    body: JSON.stringify({ quantity }),
  });
  return data;
}

export async function removeCartItem(itemId: number): Promise<CartDto> {
  const { data } = await fetchCartApi<CartDto>(`/cart/items/${itemId}/`, {
    method: "DELETE",
  });
  return data;
}

export async function clearCartApi(): Promise<CartDto> {
  const { data } = await fetchCartApi<CartDto>("/cart/clear/", {
    method: "DELETE",
  });
  return data;
}

export function cartExportPdfUrl(): string {
  return `${getApiBase()}/cart/export/pdf/`;
}

export function cartExportXlsxUrl(): string {
  return `${getApiBase()}/cart/export/xlsx/`;
}

export async function fetchCartExport(
  type: "pdf" | "xlsx",
): Promise<Blob> {
  const path = type === "pdf" ? "/cart/export/pdf/" : "/cart/export/xlsx/";
  const url = `${getApiBase()}${path}`;
  const res = await fetch(url, {
    credentials: "include",
    headers: cartSessionHeaders(),
  });
  syncCartSessionFromResponse(res);
  if (!res.ok) throw new Error("Export failed");
  return res.blob();
}
