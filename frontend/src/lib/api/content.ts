import type { ContentPage, FAQItem, NewsPost, NewsPostDetail, PaginatedResponse, SiteSettings } from "@/lib/types";

import { fetchApi, toSearchParams } from "./client";

export async function getFAQ(limit?: number): Promise<FAQItem[]> {
  try {
    const data = await fetchApi<PaginatedResponse<FAQItem>>("/faq/");
    return limit ? data.results.slice(0, limit) : data.results;
  } catch {
    return [];
  }
}

export async function getLatestNews(limit = 3): Promise<NewsPost[]> {
  try {
    const data = await fetchApi<PaginatedResponse<NewsPost>>("/news/", { revalidate: 600 });
    return data.results.slice(0, limit);
  } catch {
    return [];
  }
}

export async function getNewsList(page = 1): Promise<PaginatedResponse<NewsPost>> {
  return fetchApi<PaginatedResponse<NewsPost>>("/news/", {
    params: toSearchParams({ page }),
    revalidate: 600,
  });
}

export async function getNewsDetail(slug: string): Promise<NewsPostDetail | null> {
  try {
    return await fetchApi<NewsPostDetail>(`/news/${slug}/`, { revalidate: 600 });
  } catch {
    return null;
  }
}

export async function getPage(slug: string): Promise<ContentPage | null> {
  try {
    return await fetchApi<ContentPage>(`/pages/${slug}/`, { revalidate: 3600 });
  } catch {
    return null;
  }
}

export async function getSiteSettings(): Promise<SiteSettings | null> {
  try {
    return fetchApi<SiteSettings>("/settings/", { revalidate: 86400 });
  } catch {
    return null;
  }
}
