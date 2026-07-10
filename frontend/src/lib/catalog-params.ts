export const CATALOG_FILTER_KEYS = [
  "type",
  "current",
  "current_min",
  "current_max",
  "coil",
  "coil_min",
  "coil_max",
  "poles",
  "execution",
  "product_type",
  "series",
  "climate",
  "application",
  "doc",
  "page",
  "page_size",
  "ordering",
  "view",
] as const;

export type CatalogViewMode = "grid" | "list";

export interface CatalogSearchParams {
  type?: string[];
  current?: string[];
  current_min?: string;
  current_max?: string;
  coil?: string[];
  coil_min?: string;
  coil_max?: string;
  poles?: string[];
  execution?: string[];
  product_type?: string[];
  series?: string[];
  climate?: string[];
  application?: string[];
  doc?: string[];
  page?: string;
  page_size?: string;
  ordering?: string;
  view?: CatalogViewMode;
}

function parseMulti(raw: Record<string, string | string[] | undefined>, key: string): string[] | undefined {
  const v = raw[key];
  if (!v) return undefined;
  const parts = (Array.isArray(v) ? v : [v]).flatMap((item) =>
    item.split(",").map((s) => s.trim()).filter(Boolean),
  );
  return parts.length ? parts : undefined;
}

function parseSingle(raw: Record<string, string | string[] | undefined>, key: string): string | undefined {
  const v = raw[key];
  const s = Array.isArray(v) ? v[0] : v;
  return s || undefined;
}

export function parseCatalogParams(raw: Record<string, string | string[] | undefined>): CatalogSearchParams {
  return {
    type: parseMulti(raw, "type"),
    current: parseMulti(raw, "current"),
    current_min: parseSingle(raw, "current_min"),
    current_max: parseSingle(raw, "current_max"),
    coil: parseMulti(raw, "coil"),
    coil_min: parseSingle(raw, "coil_min"),
    coil_max: parseSingle(raw, "coil_max"),
    poles: parseMulti(raw, "poles"),
    execution: parseMulti(raw, "execution"),
    product_type: parseMulti(raw, "product_type"),
    series: parseMulti(raw, "series"),
    climate: parseMulti(raw, "climate"),
    application: parseMulti(raw, "application"),
    doc: parseMulti(raw, "doc"),
    page: parseSingle(raw, "page"),
    page_size: parseSingle(raw, "page_size"),
    ordering: parseSingle(raw, "ordering"),
    view: (parseSingle(raw, "view") as CatalogViewMode) || "grid",
  };
}

export function countActiveFilters(params: CatalogSearchParams): number {
  let n = 0;
  if (params.current?.length) n += 1;
  if (params.coil?.length) n += 1;
  if (params.poles?.length) n += 1;
  if (params.execution?.length) n += 1;
  if (params.product_type?.length) n += 1;
  if (params.series?.length) n += 1;
  return n;
}

export function hasActiveFilters(params: CatalogSearchParams): boolean {
  return countActiveFilters(params) > 0;
}

export function shouldNoindexCatalogParams(params: CatalogSearchParams): boolean {
  return (
    hasActiveFilters(params) ||
    Boolean(params.page && params.page !== "1") ||
    Boolean(params.ordering) ||
    Boolean(params.view && params.view !== "grid") ||
    Boolean(params.page_size && params.page_size !== "24")
  );
}

function appendMulti(sp: URLSearchParams, key: string, values?: string[]) {
  if (values?.length) sp.set(key, values.join(","));
}

export function toFilterApiParams(
  params: CatalogSearchParams,
  categorySlug: string,
): Record<string, string | string[]> {
  const api: Record<string, string | string[]> = { category: categorySlug };
  if (params.type?.length) api.type = params.type;
  if (params.product_type?.length) api.product_type = params.product_type;
  if (params.current?.length) api.current = params.current;
  if (params.current_min) api.current_min = params.current_min;
  if (params.current_max) api.current_max = params.current_max;
  if (params.coil?.length) api.coil = params.coil;
  if (params.coil_min) api.coil_min = params.coil_min;
  if (params.coil_max) api.coil_max = params.coil_max;
  if (params.poles?.length) api.poles = params.poles;
  if (params.execution?.length) api.execution = params.execution;
  if (params.series?.length) api.series = params.series;
  if (params.climate?.length) api.climate = params.climate;
  if (params.application?.length) api.application = params.application;
  if (params.doc?.length) api.doc = params.doc;
  if (params.page) api.page = params.page;
  if (params.page_size) api.page_size = params.page_size;
  if (params.ordering) api.ordering = params.ordering;
  return api;
}

export function toApiParams(params: CatalogSearchParams, categorySlug: string): Record<string, string> {
  const api: Record<string, string> = { category: categorySlug };
  if (params.current?.length === 1) api.current = params.current[0];
  if (params.coil?.length === 1) api.coil_voltage = params.coil[0];
  if (params.poles?.length === 1) api.poles = params.poles[0];
  if (params.execution?.length === 1) api.execution = params.execution[0];
  if (params.product_type?.length === 1) api.product_type = params.product_type[0];
  if (params.series?.length === 1) api.series_code = params.series[0];
  if (params.page) api.page = params.page;
  if (params.page_size) api.page_size = params.page_size;
  if (params.ordering) api.ordering = params.ordering;
  return api;
}

export function toSearchApiParams(
  params: CatalogSearchParams,
  query: string,
): Record<string, string> {
  const api: Record<string, string> = { q: query };
  if (params.current?.length === 1) api.current = params.current[0];
  if (params.coil?.length === 1) api.coil_voltage = params.coil[0];
  if (params.poles?.length === 1) api.poles = params.poles[0];
  if (params.execution?.length === 1) api.execution = params.execution[0];
  if (params.product_type?.length === 1) api.product_type = params.product_type[0];
  if (params.series?.length === 1) api.series_code = params.series[0];
  if (params.page) api.page = params.page;
  if (params.page_size) api.page_size = params.page_size;
  if (params.ordering) api.ordering = params.ordering;
  return api;
}

export function buildCatalogQuery(
  base: CatalogSearchParams,
  patch: Partial<CatalogSearchParams> = {},
): string {
  const merged = { ...base, ...patch };
  const sp = new URLSearchParams();
  appendMulti(sp, "type", merged.type);
  appendMulti(sp, "current", merged.current);
  if (merged.current_min) sp.set("current_min", merged.current_min);
  if (merged.current_max) sp.set("current_max", merged.current_max);
  appendMulti(sp, "coil", merged.coil);
  if (merged.coil_min) sp.set("coil_min", merged.coil_min);
  if (merged.coil_max) sp.set("coil_max", merged.coil_max);
  appendMulti(sp, "poles", merged.poles);
  appendMulti(sp, "execution", merged.execution);
  appendMulti(sp, "product_type", merged.product_type);
  appendMulti(sp, "series", merged.series);
  appendMulti(sp, "climate", merged.climate);
  appendMulti(sp, "application", merged.application);
  appendMulti(sp, "doc", merged.doc);
  if (merged.page && merged.page !== "1") sp.set("page", merged.page);
  if (merged.page_size && merged.page_size !== "24") sp.set("page_size", merged.page_size);
  if (merged.ordering) sp.set("ordering", merged.ordering);
  if (merged.view && merged.view !== "grid") sp.set("view", merged.view);
  const qs = sp.toString();
  return qs ? `?${qs}` : "";
}

export function buildSearchQuery(
  base: CatalogSearchParams,
  q: string,
  patch: Partial<CatalogSearchParams> = {},
): string {
  const merged = { ...base, ...patch };
  const sp = new URLSearchParams({ q });
  appendMulti(sp, "current", merged.current);
  appendMulti(sp, "coil", merged.coil);
  appendMulti(sp, "poles", merged.poles);
  appendMulti(sp, "execution", merged.execution);
  appendMulti(sp, "product_type", merged.product_type);
  appendMulti(sp, "series", merged.series);
  if (merged.page && merged.page !== "1") sp.set("page", merged.page);
  if (merged.page_size && merged.page_size !== "24") sp.set("page_size", merged.page_size);
  if (merged.ordering) sp.set("ordering", merged.ordering);
  if (merged.view && merged.view !== "grid") sp.set("view", merged.view);
  return `?${sp.toString()}`;
}

export const SORT_OPTIONS = [
  { value: "sort_order", label: "По умолчанию" },
  { value: "name", label: "По названию" },
  { value: "nominal_current_a", label: "По току ↑" },
  { value: "-nominal_current_a", label: "По току ↓" },
  { value: "min_price", label: "По цене ↑" },
  { value: "-min_price", label: "По цене ↓" },
] as const;

export const PAGE_SIZE_OPTIONS = [12, 24, 48] as const;

export const EXECUTION_OPTIONS = [
  { value: "B", label: "Б" },
  { value: "BS", label: "БС" },
  { value: "S", label: "С" },
] as const;

export const PRODUCT_TYPE_OPTIONS = [
  { value: "KT", label: "КТ (переменный ток)" },
  { value: "KTP", label: "КТП (постоянный ток)" },
  { value: "KTE", label: "КТЭ (электротранспорт)" },
  { value: "ACCESSORY", label: "Аксессуары" },
  { value: "SWITCH", label: "Выключатели" },
  { value: "CAM", label: "Кулачковые элементы" },
  { value: "OTHER", label: "Прочее" },
] as const;

export const DOC_FILTER_OPTIONS = [
  { value: "passport", label: "Паспорт изделия (PDF)" },
  { value: "certificate", label: "Сертификат (ЕАС)" },
  { value: "drawing", label: "Чертёж (DWG/PDF)" },
] as const;

export const CURRENT_OPTIONS = [80, 100, 125, 160, 250, 400, 630, 1000] as const;

export const COIL_OPTIONS = [36, 110, 117, 220, 380] as const;

export const POLES_OPTIONS = [2, 3] as const;

export const SERIES_OPTIONS = ["6000", "6600", "7200"] as const;

export const STORAGE_KEY_PREFIX = "catalog-filters:";

export function saveFiltersToSession(basePath: string, params: CatalogSearchParams): void {
  try {
    sessionStorage.setItem(`${STORAGE_KEY_PREFIX}${basePath}`, JSON.stringify(params));
  } catch {
    /* ignore quota errors */
  }
}

export function loadFiltersFromSession(basePath: string): CatalogSearchParams | null {
  try {
    const raw = sessionStorage.getItem(`${STORAGE_KEY_PREFIX}${basePath}`);
    return raw ? (JSON.parse(raw) as CatalogSearchParams) : null;
  } catch {
    return null;
  }
}
