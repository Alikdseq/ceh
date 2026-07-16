/** Preferred order for coil voltage chips in product cards (catalog standard). */
export const COIL_VOLTAGE_DISPLAY_ORDER = [220, 380, 36, 127, 660] as const;

export function sortCoilVoltages(values: number[]): number[] {
  const unique = [...new Set(values)];
  return unique.sort((a, b) => {
    const ia = COIL_VOLTAGE_DISPLAY_ORDER.indexOf(a as (typeof COIL_VOLTAGE_DISPLAY_ORDER)[number]);
    const ib = COIL_VOLTAGE_DISPLAY_ORDER.indexOf(b as (typeof COIL_VOLTAGE_DISPLAY_ORDER)[number]);
    if (ia !== -1 && ib !== -1) return ia - ib;
    if (ia !== -1) return -1;
    if (ib !== -1) return 1;
    return a - b;
  });
}

/** Normalize spec text: fix duplicate «В», sort voltages ascending in comma lists. */
export function formatCoilSpecValue(raw: string): string {
  let text = raw.replace(/\s+/g, " ").trim();
  text = text.replace(/(\d+)\s*В\s*В/gi, "$1 В");
  text = text.replace(/(\d+)\s*[Vv]\b/g, "$1 В");

  const voltages = [...text.matchAll(/(\d+)\s*В/g)].map((m) => Number(m[1]));
  if (voltages.length <= 1) return text;

  const sorted = sortCoilVoltages(voltages);
  return sorted.map((v) => `${v} В`).join(", ");
}
