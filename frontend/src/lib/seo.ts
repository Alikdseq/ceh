import type { Metadata } from "next";

import type { Category, ContentPage } from "@/lib/types";
import { productImageSrc } from "@/lib/utils";

const SITE_URL = (process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000").replace(/\/$/, "");
const SITE_NAME = "Электроконтактор";

export function getSiteUrl(): string {
  return SITE_URL;
}

export function getMetadataBase(): URL {
  return new URL(SITE_URL);
}

export interface PageSeoInput {
  title: string;
  description: string;
  path?: string;
  ogImage?: string;
  noindex?: boolean;
  canonical?: string;
}

export function buildPageMetadata({
  title,
  description,
  path,
  ogImage,
  noindex,
  canonical,
}: PageSeoInput): Metadata {
  const url = canonical
    ? canonical.startsWith("http")
      ? canonical
      : `${SITE_URL}${canonical.startsWith("/") ? canonical : `/${canonical}`}`
    : path
      ? `${SITE_URL}${path.startsWith("/") ? path : `/${path}`}`
      : SITE_URL;
  const image = ogImage || `${SITE_URL}/placeholder-product.svg`;

  return {
    title,
    description,
    ...(noindex ? { robots: { index: false, follow: true } } : {}),
    alternates: { canonical: url },
    openGraph: {
      title,
      description,
      url,
      siteName: SITE_NAME,
      locale: "ru_RU",
      type: "website",
      images: [{ url: image, alt: title }],
    },
    twitter: {
      card: "summary_large_image",
      title,
      description,
      images: [image],
    },
  };
}

export function fallbackCategoryTitle(name: string): string {
  return `${name} — купить от производителя | Электроконтактор`;
}

export function fallbackCategoryDescription(name: string): string {
  return `${name}: цены, характеристики, документация. Прямые поставки с завода во Владикавказе.`;
}

export function fallbackProductTitle(name: string): string {
  return `${name} — характеристики, цена | Купить у производителя`;
}

export function fallbackProductDescription(product: {
  name: string;
  nominal_current_a?: number | null;
  poles?: number | null;
  price_from?: string | null;
}): string {
  const parts = [product.name];
  if (product.nominal_current_a) {
    parts.push(`${product.nominal_current_a}А`);
  }
  if (product.poles) {
    parts.push(`${product.poles} полюса`);
  }
  let desc = parts.join(". ");
  if (product.price_from && parseFloat(product.price_from) > 0) {
    desc += `. Цена от ${product.price_from} ₽`;
  }
  desc += ". Паспорт, чертежи, заявка на поставку.";
  return desc;
}

export function buildCategoryMetadata(
  category: Pick<
    Category,
    "name" | "meta_title" | "meta_description" | "description" | "noindex" | "canonical_override"
  >,
  slugPath: string[],
  options: { noindexParams?: boolean } = {},
): Metadata {
  const path = `/catalog/${slugPath.join("/")}/`;
  const title = category.meta_title || fallbackCategoryTitle(category.name);
  const description =
    category.meta_description ||
    category.description ||
    fallbackCategoryDescription(category.name);
  const noindex = Boolean(category.noindex || options.noindexParams);
  const canonical = category.canonical_override || path;

  return buildPageMetadata({ title, description, path, noindex, canonical });
}

export function buildProductMetadata(
  product: {
    name: string;
    slug: string;
    meta_title?: string;
    meta_description?: string;
    short_description?: string;
    nominal_current_a?: number | null;
    poles?: number | null;
    price_from?: string | null;
    primary_image?: { url: string | null } | null;
    category_path?: string[];
    category_slug?: string;
    series_code?: string;
    product_type?: string;
  },
  categoryPath?: string[],
): Metadata {
  const pathSlugs = categoryPath?.length
    ? categoryPath
    : product.category_path?.length
      ? product.category_path
      : product.category_slug
        ? [product.category_slug]
        : [];
  const path = `/catalog/${[...pathSlugs, product.slug].join("/")}/`;
  const title = product.meta_title || fallbackProductTitle(product.name);
  const description =
    product.meta_description ||
    product.short_description ||
    fallbackProductDescription(product);
  const ogImage =
    productImageSrc(product.primary_image?.url, {
      name: product.name,
      slug: product.slug,
      series_code: product.series_code,
      product_type: product.product_type,
    }) || undefined;

  return buildPageMetadata({ title, description, path, ogImage });
}

export function buildCmsPageMetadata(
  page: Pick<ContentPage, "meta_title" | "meta_description" | "title">,
  path: string,
): Metadata {
  const title = page.meta_title || page.title;
  const description = page.meta_description || page.title;
  return buildPageMetadata({ title, description, path });
}

export function buildNewsMetadata(
  post: { meta_title?: string; meta_description?: string; title: string; excerpt?: string },
  slug: string,
): Metadata {
  const path = `/news/${slug}/`;
  const title = post.meta_title || post.title;
  const description = post.meta_description || post.excerpt || post.title;
  return buildPageMetadata({ title, description, path });
}

export function buildSearchMetadata(query?: string): Metadata {
  const title = query?.trim() ? `Поиск: ${query.trim()}` : "Поиск по каталогу";
  const description = query?.trim()
    ? `Результаты поиска «${query.trim()}» в каталоге Электроконтактор.`
    : "Поиск контакторов и аппаратуры по каталогу завода Электроконтактор.";
  return buildPageMetadata({
    title,
    description,
    path: "/search/",
    noindex: true,
  });
}

export function buildHomeMetadata(): Metadata {
  return buildPageMetadata({
    title: "Электроконтактор — производитель контакторов КТ, КТП, КТЭ",
    description:
      "АО «Владикавказский завод «Электроконтактор» — производитель контакторов с 1956 года. Прямые поставки, публичные цены, маркировка «Честный знак».",
    path: "/",
  });
}
