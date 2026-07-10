import type { ProductVariant } from "@/lib/types";

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
  return pool[0] ?? variants.find((v) => v.is_default) ?? variants[0];
}

export function listAuxContacts(variants: ProductVariant[]): string[] {
  return [
    ...new Set(
      variants.map((v) => v.aux_contacts).filter((value): value is string => Boolean(value)),
    ),
  ];
}
