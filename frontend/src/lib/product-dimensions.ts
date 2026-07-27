/** PDF with overall dimensions for KT contactors (series 6013–6053). */
export const CONTACTOR_DIMENSIONS_PDF = "/docs/gabarity-kontaktory-6013-6053.pdf";

export function isDimensionsSpecKey(key: string): boolean {
  const normalized = key.toLowerCase();
  return (
    key === "overall_dimensions" ||
    normalized.includes("dimension") ||
    normalized.includes("gabarit")
  );
}
