import type { PaginatedResponse, ProductGroup, ProductGroupDetail } from "@/lib/types";

import { fetchApi, toSearchParams } from "./client";

export async function getProducts(
  params?: Record<string, string | number | boolean>,
): Promise<PaginatedResponse<ProductGroup>> {
  return fetchApi<PaginatedResponse<ProductGroup>>("/products/", {
    params: toSearchParams(params),
    revalidate: 60,
  });
}

export async function getProduct(slug: string): Promise<ProductGroupDetail> {
  return fetchApi<ProductGroupDetail>(`/products/${slug}/`, { revalidate: 600 });
}

export async function tryGetProduct(slug: string): Promise<ProductGroupDetail | null> {
  try {
    return await getProduct(slug);
  } catch {
    return null;
  }
}

export async function getAccessories(limit = 6): Promise<ProductGroup[]> {
  try {
    const data = await getProducts({ category: "aksessuary-kontaktorov", page_size: limit });
    return data.results;
  } catch {
    return [];
  }
}

export async function getFeaturedProducts(limit = 4): Promise<ProductGroup[]> {
  try {
    const featured = await getProducts({ featured: true, page_size: limit });
    if (featured.results.length > 0) return featured.results;
    const fallback = await getProducts({ page_size: limit, ordering: "nominal_current_a" });
    return fallback.results;
  } catch {
    return [];
  }
}
