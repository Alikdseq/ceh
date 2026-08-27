import type { PriceListSection } from "@/lib/shareholders-docs";
import { fetchApi } from "./client";

export async function getPriceList(): Promise<PriceListSection[]> {
  return fetchApi<PriceListSection[]>("/pricelist/", { cache: "no-store" });
}

export function getPriceListPdfUrl(): string {
  return "/api/v1/pricelist/export/pdf/";
}
