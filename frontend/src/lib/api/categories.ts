import type { Category } from "@/lib/types";
import { unstable_noStore as noStore } from "next/cache";

import { fetchApi } from "./client";

export async function getCategories(): Promise<Category[]> {
  noStore();
  try {
    return await fetchApi<Category[]>("/categories/", { cache: "no-store" });
  } catch {
    return [];
  }
}
