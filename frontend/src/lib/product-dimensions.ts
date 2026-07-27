/** Drawing with overall dimensions for KT/KTP contactors (static under /photos/). */
export const CONTACTOR_DIMENSIONS_IMAGE = "/photos/gabariti-kontaktory.png";

export function isDimensionsSpecKey(key: string): boolean {
  const normalized = key.toLowerCase();
  return (
    key === "overall_dimensions" ||
    normalized.includes("dimension") ||
    normalized.includes("gabarit")
  );
}
