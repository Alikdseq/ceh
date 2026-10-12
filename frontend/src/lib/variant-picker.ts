import type { ProductVariant } from "@/lib/types";

function variantPrice(value: string | number): number {
  const num = typeof value === "string" ? parseFloat(value) : value;
  return Number.isFinite(num) ? num : 0;
}

function pickFromPool(pool: ProductVariant[]): ProductVariant | undefined {
  if (!pool.length) return undefined;
  return pool.find((v) => variantPrice(v.price) > 0) ?? pool[0];
}

export function pickProductVariant(
  variants: ProductVariant[],
  execution: string | null,
  coil: number | null,
  auxContacts: string | null,
): ProductVariant | undefined {
  let pool = variants;
  if (execution) pool = pool.filter((v) => v.execution === execution);
  if (coil != null) pool = pool.filter((v) => v.coil_voltage_v === coil);
  if (auxContacts) pool = pool.filter((v) => v.aux_contacts === auxContacts);
  return (
    pickFromPool(pool) ??
    pickFromPool(variants.filter((v) => v.is_default)) ??
    pickFromPool(variants)
  );
}

export function listAuxContacts(variants: ProductVariant[]): string[] {
  return [
    ...new Set(
      variants.map((v) => v.aux_contacts).filter((value): value is string => Boolean(value)),
    ),
  ];
}

const EXECUTION_ORDER = ["B", "BS", "S", "NONE"] as const;

export function listExecutions(variants: ProductVariant[]): string[] {
  const codes = [...new Set(variants.map((v) => v.execution).filter(Boolean))];
  return codes.sort(
    (a, b) =>
      (EXECUTION_ORDER.indexOf(a as (typeof EXECUTION_ORDER)[number]) + 1 || 99) -
      (EXECUTION_ORDER.indexOf(b as (typeof EXECUTION_ORDER)[number]) + 1 || 99),
  );
}
