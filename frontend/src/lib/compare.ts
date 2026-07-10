"use client";

const COMPARE_KEY = "compare_ids";
const MAX_COMPARE = 4;
const COMPARE_EVENT = "compare-updated";

export function getCompareIds(): number[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(COMPARE_KEY);
    const parsed = raw ? (JSON.parse(raw) as unknown) : [];
    if (!Array.isArray(parsed)) return [];
    return parsed.filter((id): id is number => typeof id === "number").slice(0, MAX_COMPARE);
  } catch {
    return [];
  }
}

export function setCompareIds(ids: number[]): void {
  const unique = [...new Set(ids)].slice(0, MAX_COMPARE);
  localStorage.setItem(COMPARE_KEY, JSON.stringify(unique));
  window.dispatchEvent(new CustomEvent(COMPARE_EVENT));
}

export function getCompareCount(): number {
  return getCompareIds().length;
}

export function addToCompare(variantId: number): boolean {
  const ids = getCompareIds();
  if (ids.includes(variantId)) return true;
  if (ids.length >= MAX_COMPARE) return false;
  setCompareIds([...ids, variantId]);
  return true;
}

export function removeFromCompare(variantId: number): void {
  setCompareIds(getCompareIds().filter((id) => id !== variantId));
}

export function clearCompare(): void {
  localStorage.removeItem(COMPARE_KEY);
  window.dispatchEvent(new CustomEvent(COMPARE_EVENT));
}

export { COMPARE_EVENT, MAX_COMPARE };
