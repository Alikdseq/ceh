import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

import { resolveStaticProductImage, type ProductImageContext } from "@/lib/product-images";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatPrice(value: string | number | null | undefined): string {
  if (value === null || value === undefined || value === "") return "—";
  const num = typeof value === "string" ? parseFloat(value) : value;
  if (Number.isNaN(num) || num <= 0) return "по запросу";
  return new Intl.NumberFormat("ru-RU", {
    style: "currency",
    currency: "RUB",
    maximumFractionDigits: 0,
  }).format(num);
}

export function formatDate(iso: string): string {
  return new Intl.DateTimeFormat("ru-RU", {
    day: "numeric",
    month: "long",
    year: "numeric",
  }).format(new Date(iso));
}

export const PLACEHOLDER_PRODUCT_SRC = "/placeholder-product.svg";

/** Encode Cyrillic/spaces in local public asset paths for reliable loading. */
export function publicAssetSrc(path: string): string {
  if (!path.startsWith("/")) return path;
  try {
    const decoded = decodeURI(path);
    return encodeURI(decoded);
  } catch {
    return path;
  }
}

export function productImageSrc(
  url: string | undefined | null,
  context?: ProductImageContext,
): string {
  if (context) {
    const staticUrl = resolveStaticProductImage(context);
    if (staticUrl) return staticUrl;
  }
  if (!url || url.includes("placeholder-product")) return PLACEHOLDER_PRODUCT_SRC;
  return url;
}

/** next/image: skip optimizer for local static assets (SVG, /tovar/, photos) */
export function productImageUnoptimized(src: string): boolean {
  if (src === PLACEHOLDER_PRODUCT_SRC || src.endsWith(".svg")) return true;
  if (src.includes("/tovar/") || src.includes("/photos/")) return true;
  return /\.(jpe?g|png|webp)(\?|$)/i.test(src);
}

export function executionLabel(code: string): string {
  return ({ B: "Б", BS: "БС", S: "С", NONE: "—" } as Record<string, string>)[code] ?? code;
}

export function productTypeLabel(code: string): string {
  return (
    {
      KT: "КТ (переменный ток)",
      KTP: "КТП (постоянный ток)",
      KTE: "КТЭ (электротранспорт)",
      ACCESSORY: "Аксессуар",
      SWITCH: "Выключатель",
      CAM: "Кулачковый элемент",
      OTHER: "Прочее",
    } as Record<string, string>
  )[code] ?? code;
}

export function coilTypeLabel(code: string): string {
  return (
    {
      AC: "Переменный ток",
      DC: "Постоянный ток",
      NONE: "—",
    } as Record<string, string>
  )[code] ?? code;
}

export function specKeyLabel(key: string): string {
  const labels: Record<string, string> = {
    nominal_current: "Номинальный ток",
    nominal_voltage: "Номинальное напряжение",
    frequency: "Номинальная частота",
    poles: "Число полюсов",
    application_category: "Категория применения",
    coil_voltage_ac: "Напряжение катушки (переменный ток)",
    coil_voltage_dc: "Напряжение катушки (постоянный ток)",
    current: "Номинальный ток",
    voltage: "Номинальное напряжение",
    weight_net: "Масса нетто",
    weight_gross: "Масса брутто",
    aux_contacts: "Вспомогательные контакты",
    series_code: "Серия",
    product_type: "Тип продукции",
    execution: "Исполнение",
    coil_type: "Тип катушки",
    coil_voltage: "Напряжение катушки",
    stock_status: "Наличие",
  };
  return labels[key] ?? key.replace(/_/g, " ");
}
