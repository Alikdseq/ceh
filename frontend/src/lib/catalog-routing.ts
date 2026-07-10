import { tryGetProduct } from "@/lib/api";
import { findCategoryByPath } from "@/lib/categories";
import type { Category } from "@/lib/types";
import type { ProductGroupDetail } from "@/lib/types";

export type CatalogRouteResult =
  | { type: "product"; product: ProductGroupDetail }
  | { type: "category"; slugPath: string[] }
  | { type: "not_found" };

export async function resolveCatalogRoute(
  slugPath: string[],
  categories: Category[],
): Promise<CatalogRouteResult> {
  if (slugPath.length === 0) {
    return { type: "not_found" };
  }

  const lastSegment = slugPath[slugPath.length - 1];
  const product = await tryGetProduct(lastSegment);
  if (product) {
    return { type: "product", product };
  }

  const category = findCategoryByPath(categories, slugPath);
  if (category) {
    return { type: "category", slugPath };
  }

  return { type: "not_found" };
}
