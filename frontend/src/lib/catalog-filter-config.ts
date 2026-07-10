/** Which catalog sidebar filters are shown per root category (and descendants). */

export type CatalogFilterKey =
  | "current"
  | "coil"
  | "poles"
  | "execution"
  | "product_type"
  | "series";

const FILTERS_BY_ROOT: Record<string, CatalogFilterKey[]> = {
  "kontaktory-kt": ["current", "coil", "poles", "execution", "series"],
  "kontaktory-ktp": ["current", "coil", "poles", "execution", "series"],
  "kontaktory-kte": ["current", "series"],
  "aksessuary-kontaktorov": [],
  vyklyuchateli: [],
  "kulachkovye-elementy": [],
  "paketnye-pereklyuchateli": [],
};

/** Root catalog slug from category path (first segment). */
export function getCatalogRootSlug(slugPath: string[]): string | null {
  return slugPath[0] ?? null;
}

export function getAvailableFilters(slugPath: string[]): CatalogFilterKey[] {
  const root = getCatalogRootSlug(slugPath);
  if (!root) return [];
  return FILTERS_BY_ROOT[root] ?? [];
}

export function hasCatalogFilters(slugPath: string[]): boolean {
  return getAvailableFilters(slugPath).length > 0;
}
