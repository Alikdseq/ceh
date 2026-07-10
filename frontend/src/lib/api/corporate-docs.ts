import type { ShareholderDocument } from "@/lib/shareholders-docs";
import { fetchApi } from "./client";

export async function getCorporateDocuments(
  category: "affilr" | "raskrinfo",
): Promise<ShareholderDocument[]> {
  try {
    return await fetchApi<ShareholderDocument[]>(`/corporate-docs/?category=${category}`, {
      revalidate: 3600,
    });
  } catch {
    return [];
  }
}
