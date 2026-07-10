import type { PaginatedResponse, ProductGroup } from "@/lib/types";

import { fetchApi, fetchApiClient, toSearchParams } from "./client";

export interface SearchSuggestion {
  name: string;
  sku: string;
  category_name: string;
  category_slug: string;
  product_slug: string;
  variant_id: number | null;
}

export interface SearchSuggestResponse {
  query: string;
  suggestions: SearchSuggestion[];
}

export interface SearchPaginatedResponse extends PaginatedResponse<ProductGroup> {
  query: string;
}

export async function searchProducts(
  params: Record<string, string | number | boolean>,
): Promise<SearchPaginatedResponse> {
  return fetchApi<SearchPaginatedResponse>("/search/", {
    params: toSearchParams(params),
    cache: "no-store",
  });
}

export async function getSearchSuggestions(q: string): Promise<SearchSuggestResponse> {
  return fetchApiClient<SearchSuggestResponse>("/search/suggest/", {
    params: new URLSearchParams({ q }),
  });
}
