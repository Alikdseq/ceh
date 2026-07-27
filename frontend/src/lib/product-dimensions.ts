/** Drawing with overall dimensions for KT/KTP contactors. */
export const CONTACTOR_DIMENSIONS_IMAGE = "/docs/gabariti.png";

export function isDimensionsSpecKey(key: string): boolean {
  const normalized = key.toLowerCase();
  return (
    key === "overall_dimensions" ||
    normalized.includes("dimension") ||
    normalized.includes("gabarit")
  );
}
