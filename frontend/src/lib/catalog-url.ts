import type { Category } from "./types";
import { getCategoryPathSlugs } from "./categories";

/** Full public URL path for a product card (includes parent categories). */
export function catalogProductPath(
  product: {
    slug: string;
    category_path?: string[];
    category_slug?: string;
  },
  categories?: Category[],
): string {
  const segments =
    product.category_path?.length
      ? product.category_path
      : product.category_slug && categories?.length
        ? getCategoryPathSlugs(categories, product.category_slug)
        : product.category_slug
          ? [product.category_slug]
          : [];
  return `/catalog/${[...segments, product.slug].join("/")}`;
}

export function catalogProductHref(
  product: Parameters<typeof catalogProductPath>[0],
  categories?: Category[],
): string {
  return catalogProductPath(product, categories);
}

export function normalizeCatalogPath(path: string): string {
  const trimmed = path.replace(/\/+$/, "");
  return trimmed.startsWith("/") ? trimmed : `/${trimmed}`;
}

export function catalogPathsEqual(a: string, b: string): boolean {
  return normalizeCatalogPath(a) === normalizeCatalogPath(b);
}
