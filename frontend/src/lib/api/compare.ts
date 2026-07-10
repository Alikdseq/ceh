import type { CompareResponse } from "@/lib/types";

import { fetchApi, toSearchParams } from "./client";

export async function getCompareData(ids: number[]): Promise<CompareResponse | null> {
  if (!ids.length) return null;
  try {
    return await fetchApi<CompareResponse>("/compare/", {
      params: toSearchParams({ ids: ids.join(",") }),
      revalidate: 300,
    });
  } catch {
    return null;
  }
}
