import type { CaseStudyDetail, CaseStudyListItem, DeliveryCity, PaginatedResponse } from "@/lib/types";

import { fetchApi } from "./client";

export async function getCaseStudies(): Promise<CaseStudyListItem[]> {
  try {
    const data = await fetchApi<PaginatedResponse<CaseStudyListItem> | CaseStudyListItem[]>("/cases/", {
      revalidate: 3600,
    });
    if (Array.isArray(data)) return data;
    return data.results ?? [];
  } catch {
    return [];
  }
}

export async function getCaseStudy(slug: string): Promise<CaseStudyDetail | null> {
  try {
    return await fetchApi<CaseStudyDetail>(`/cases/${slug}/`, { revalidate: 3600 });
  } catch {
    return null;
  }
}

export async function getDeliveryCities(): Promise<DeliveryCity[]> {
  try {
    const data = await fetchApi<PaginatedResponse<DeliveryCity> | DeliveryCity[]>("/delivery/", {
      revalidate: 3600,
    });
    if (Array.isArray(data)) return data;
    return data.results ?? [];
  } catch {
    return [];
  }
}

export async function getDeliveryCity(slug: string): Promise<DeliveryCity | null> {
  try {
    return await fetchApi<DeliveryCity>(`/delivery/${slug}/`, { revalidate: 3600 });
  } catch {
    return null;
  }
}
