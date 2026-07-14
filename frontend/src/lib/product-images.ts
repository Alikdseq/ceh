/** Static product photos from /public/tovar and /public/photos. */

export interface ProductImageContext {
  series_code?: string;
  product_type?: string;
  name?: string;
  slug?: string;
  sku_code?: string;
  execution?: string;
  coil_voltage_v?: number | null;
}

type ProductExecution = "B" | "BS" | "S" | "NONE";

interface ProductIdentity {
  product_type: "KT" | "KTP";
  series: string;
  execution: ProductExecution;
  coil36v: boolean;
}

/** Product cards that need a 90° clockwise photo rotation in the UI. */
const ROTATED_PRODUCTS: ProductIdentity[] = [
  { product_type: "KT", series: "6014", execution: "B", coil36v: false },
  { product_type: "KT", series: "6014", execution: "BS", coil36v: false },
  { product_type: "KT", series: "6032", execution: "B", coil36v: false },
  { product_type: "KT", series: "6032", execution: "BS", coil36v: false },
  { product_type: "KT", series: "6043", execution: "B", coil36v: false },
  { product_type: "KT", series: "6043", execution: "BS", coil36v: false },
  { product_type: "KT", series: "6053", execution: "B", coil36v: false },
  { product_type: "KT", series: "6053", execution: "BS", coil36v: false },
  { product_type: "KT", series: "6623", execution: "S", coil36v: false },
  { product_type: "KT", series: "6633", execution: "NONE", coil36v: false },
  { product_type: "KT", series: "6642", execution: "S", coil36v: false },
  { product_type: "KT", series: "7223", execution: "NONE", coil36v: true },
  { product_type: "KTP", series: "6012", execution: "B", coil36v: false },
  { product_type: "KTP", series: "6012", execution: "BS", coil36v: false },
  { product_type: "KTP", series: "6013", execution: "B", coil36v: false },
  { product_type: "KTP", series: "6013", execution: "BS", coil36v: false },
  { product_type: "KTP", series: "6014", execution: "B", coil36v: false },
  { product_type: "KTP", series: "6014", execution: "BS", coil36v: false },
  { product_type: "KTP", series: "6032", execution: "B", coil36v: false },
  { product_type: "KTP", series: "6032", execution: "BS", coil36v: false },
  { product_type: "KTP", series: "6043", execution: "B", coil36v: false },
  { product_type: "KTP", series: "6043", execution: "BS", coil36v: false },
  { product_type: "KTP", series: "6633", execution: "NONE", coil36v: false },
  { product_type: "KTP", series: "6633", execution: "B", coil36v: false },
  { product_type: "KTP", series: "6633", execution: "S", coil36v: false },
];

const TOVAR_FILES = [
  "Кт6012.JPG",
  "КТ6013.JPG",
  "КТ6014.JPG",
  "КТ6022.JPG",
  "КТ6023.JPG",
  "Кт6024.JPG",
  "Кт6032.JPG",
  "Кт6032(2).JPG",
  "КТ6033.JPG",
  "КТ6033(2).JPG",
  "КТ6042.JPG",
  "КТ6043.JPG",
  "КТ6053.JPG",
  "КТ6613.JPG",
  "КТ6623.JPG",
  "КТ6632.JPG",
  "КТ6632(2).JPG",
  "КТ6633.JPG",
  "КТ6633(2).JPG",
  "Кт6642.JPG",
  "Кт6643.JPG",
  "КТ6653.JPG",
  "КТ7223.JPG",
  "КТ7223(2).JPG",
  "КТП6012.JPG",
  "КТП6013.JPG",
  "КТП6014.JPG",
  "КТП6022.JPG",
  "КТП6022(2).JPG",
  "КТП6024.JPG",
  "КТП6032.JPG",
  "КТП6032(2).JPG",
  "КТП6033.JPG",
  "КТП6033(2).JPG",
  "КТП6042.JPG",
  "КТП6042(2).JPG",
  "КТП6043.JPG",
  "КТП6043(2).JPG",
  "КТП6633.JPG",
  "КТП6633(2).JPG",
] as const;

/** Explicit name/sku → photo mapping for non-series products. */
const NAMED_IMAGES: Array<{ pattern: RegExp; url: string; gallery?: string[] }> = [
  {
    pattern: /блок\s*контакт/i,
    url: "/tovar/блокконтактов.jpeg",
  },
  {
    pattern: /выключатель\s*путев|впк\s*3110/i,
    url: "/tovar/Выклю Путевой 1.jpeg",
    gallery: ["/tovar/Выклю Путевой 1.jpeg", "/tovar/Вык пут 2.jpeg"],
  },
  {
    pattern: /эу[\s-]*5/i,
    url: "/tovar/ЭУ5.jpg",
  },
  {
    pattern: /кэ[\s-]*46/i,
    url: "/tovar/КЭ-46.jpg",
  },
  {
    pattern: /кэ[\s-]*47/i,
    url: "/tovar/КЭ-47.jpg",
  },
  {
    pattern: /кэ[\s-]*54/i,
    url: "/tovar/КЭ-54.png",
  },
  {
    pattern: /кэ[\s-]*61/i,
    url: "/photos/кэ61.png",
  },
];

function tovarPublicUrl(filename: string): string {
  return `/tovar/${encodeURIComponent(filename)}`;
}

function fileToImageKey(filename: string): string | null {
  const base = filename.replace(/\.jpg$/i, "").replace(/\(2\)$/i, "");
  const upper = base.toUpperCase();
  if (upper.startsWith("КТП")) return `KTP${upper.slice(3)}`;
  if (upper.startsWith("КТ")) return `KT${upper.slice(2)}`;
  return null;
}

function buildImageMap(): Map<string, string[]> {
  const map = new Map<string, string[]>();
  for (const file of TOVAR_FILES) {
    const key = fileToImageKey(file);
    if (!key) continue;
    const url = tovarPublicUrl(file);
    const list = map.get(key) ?? [];
    list.push(url);
    map.set(key, list);
  }
  for (const [key, urls] of map) {
    urls.sort((a, b) => {
      const aAlt = a.includes("%282%29") ? 1 : 0;
      const bAlt = b.includes("%282%29") ? 1 : 0;
      return aAlt - bAlt;
    });
    map.set(key, urls);
  }
  return map;
}

const IMAGE_MAP = buildImageMap();

function productLabel(context: ProductImageContext): string {
  return [context.name, context.sku_code, context.slug].filter(Boolean).join(" ");
}

function resolveNamedImage(context: ProductImageContext): { url: string; gallery?: string[] } | null {
  const label = productLabel(context);
  if (!label) return null;
  for (const entry of NAMED_IMAGES) {
    if (entry.pattern.test(label)) {
      return { url: entry.url, gallery: entry.gallery };
    }
  }
  return null;
}

function extractSeriesCode(context: ProductImageContext): string | null {
  const fromField = context.series_code?.replace(/\D/g, "");
  if (fromField && fromField.length >= 4) return fromField.slice(0, 4);

  const sources = [context.sku_code, context.name, context.slug].filter(Boolean) as string[];
  for (const source of sources) {
    const ktp = source.match(/КТП[\s-]*(\d{4})/i);
    if (ktp) return ktp[1];
    const kt = source.match(/КТ[\s-]*(\d{4})/i);
    if (kt) return kt[1];
    const digits = source.match(/(\d{4})/);
    if (digits) return digits[1];
  }
  return null;
}

function resolveImageKey(context: ProductImageContext): string | null {
  const series = extractSeriesCode(context);
  if (!series) return null;

  const type = context.product_type?.toUpperCase();
  if (type === "KTP") return `KTP${series}`;
  if (type === "KT") return `KT${series}`;

  const name = context.name ?? context.sku_code ?? "";
  if (/КТП/i.test(name)) return `KTP${series}`;
  if (/КТ/i.test(name)) return `KT${series}`;

  return null;
}

export function resolveStaticProductImage(context: ProductImageContext): string | null {
  const named = resolveNamedImage(context);
  if (named) return named.url;

  const key = resolveImageKey(context);
  if (!key) return null;
  return IMAGE_MAP.get(key)?.[0] ?? null;
}

export function resolveStaticProductGallery(context: ProductImageContext): string[] {
  const named = resolveNamedImage(context);
  if (named) return named.gallery ?? [named.url];

  const key = resolveImageKey(context);
  if (!key) return [];
  return IMAGE_MAP.get(key) ?? [];
}

function normalizeExecution(raw: string | undefined | null): ProductExecution | null {
  if (!raw) return null;
  const value = raw.toUpperCase();
  if (value === "B" || value === "BS" || value === "S" || value === "NONE") return value;
  return null;
}

function executionFromLabel(label: string): ProductExecution {
  const compact = label.replace(/\s+/g, "").toUpperCase();
  if (compact.includes("БС")) return "BS";
  if (compact.includes("БК")) return "NONE";
  if (compact.includes("Б")) return "B";
  if (compact.includes("С")) return "S";
  return "NONE";
}

function resolveProductIdentity(context: ProductImageContext): ProductIdentity | null {
  const labels = [context.name, context.sku_code, context.slug].filter(Boolean) as string[];
  const coil36v =
    labels.some((label) => /36\s*V/i.test(label.replace(/\s+/g, ""))) ||
    context.coil_voltage_v === 36;

  for (const label of labels) {
    const compact = label.replace(/\s+/g, "").toUpperCase();
    const ktp = compact.match(/^КТП(\d{4})/);
    if (ktp) {
      return {
        product_type: "KTP",
        series: ktp[1],
        execution: normalizeExecution(context.execution) ?? executionFromLabel(compact),
        coil36v,
      };
    }
    const kt = compact.match(/^КТ(\d{4})/);
    if (kt) {
      return {
        product_type: "KT",
        series: kt[1],
        execution: normalizeExecution(context.execution) ?? executionFromLabel(compact),
        coil36v,
      };
    }
  }

  const series = context.series_code?.replace(/\D/g, "").slice(0, 4);
  const productType = context.product_type?.toUpperCase();
  if (!series || (productType !== "KT" && productType !== "KTP")) return null;

  const execution = normalizeExecution(context.execution) ??
    labels.map(executionFromLabel).find((value) => value !== "NONE") ??
    "NONE";

  return {
    product_type: productType,
    series,
    execution,
    coil36v,
  };
}

function identitiesMatch(left: ProductIdentity, right: ProductIdentity): boolean {
  return (
    left.product_type === right.product_type &&
    left.series === right.series &&
    left.execution === right.execution &&
    left.coil36v === right.coil36v
  );
}

export function shouldRotateProductImage(context?: ProductImageContext): boolean {
  if (!context) return false;
  const identity = resolveProductIdentity(context);
  if (!identity) return false;
  return ROTATED_PRODUCTS.some((rule) => identitiesMatch(rule, identity));
}

/** Tailwind class for a 90° clockwise product photo rotation. */
export function productImageRotateClass(context?: ProductImageContext): string {
  return shouldRotateProductImage(context) ? "rotate-90" : "";
}
