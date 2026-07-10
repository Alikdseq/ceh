import type { PaginatedResponse, ProductGroup } from "@/lib/types";

import { fetchApi, fetchApiClient, toSearchParams } from "./client";

export interface FacetCountMap {
  [key: string]: number | string;
}

export interface RangeFacetMeta {
  min: number | null;
  max: number | null;
  available: number[];
  counts: Record<string, number>;
}

export interface CategoryTypeFacet {
  name: string;
  count: number;
}

export interface CatalogFiltersMeta {
  category_type: Record<string, CategoryTypeFacet>;
  product_type: Record<string, number>;
  current_rating: RangeFacetMeta;
  coil_voltage: RangeFacetMeta;
  execution: Record<string, number>;
  poles: Record<string, number>;
  series: Record<string, number>;
  application: Record<string, number>;
  documentation: Record<string, number>;
}

export interface CatalogFilterResponse extends PaginatedResponse<ProductGroup> {
  status: string;
  current_page: number;
  last_page: number;
  filters_meta: CatalogFiltersMeta;
  applied_filters: Record<string, unknown>;
}

export async function getCatalogFilter(
  params: Record<string, string | number | boolean | string[]>,
): Promise<CatalogFilterResponse> {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === "" || value === null) return;
    if (Array.isArray(value)) {
      if (value.length) search.set(key, value.join(","));
    } else {
      search.set(key, String(value));
    }
  });
  return fetchApi<CatalogFilterResponse>("/catalog/filter/", {
    params: search,
    revalidate: 60,
  });
}

export async function fetchCatalogFilterClient(
  params: Record<string, string | number | boolean | string[]>,
): Promise<CatalogFilterResponse> {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === "" || value === null) return;
    if (Array.isArray(value)) {
      if (value.length) search.set(key, value.join(","));
    } else {
      search.set(key, String(value));
    }
  });
  return fetchApiClient<CatalogFilterResponse>("/catalog/filter/", { params: search });
}
