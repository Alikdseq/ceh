import type { Metadata } from "next";
import { notFound } from "next/navigation";

import {
  CategoryListing,
  generateCategoryMetadata,
} from "@/components/catalog/CategoryListing";
import { ProductDetailPage } from "@/components/product/ProductDetailPage";
import { getCategories, tryGetProduct } from "@/lib/api";
import { getCategoryPathSlugs } from "@/lib/categories";
import { buildProductMetadata } from "@/lib/seo";

interface PageProps {
  params: Promise<{ slug: string[] }>;
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}

export async function generateMetadata({ params, searchParams }: PageProps): Promise<Metadata> {
  const { slug } = await params;
  const sp = await searchParams;
  const product = await tryGetProduct(slug[slug.length - 1] ?? "");
  if (product) {
    const categories = await getCategories();
    const categoryPath =
      product.category_path?.length
        ? product.category_path
        : getCategoryPathSlugs(categories, product.category_slug);
    return buildProductMetadata(product, categoryPath);
  }
  return generateCategoryMetadata(slug, sp);
}

export default async function CatalogCategoryPage({ params, searchParams }: PageProps) {
  const { slug } = await params;
  const sp = await searchParams;

  const lastSegment = slug[slug.length - 1];
  const product = await tryGetProduct(lastSegment);
  if (product) {
    return <ProductDetailPage product={product} />;
  }

  const categories = await getCategories();
  const { findCategoryByPath } = await import("@/lib/categories");
  const category = findCategoryByPath(categories, slug);
  if (!category) {
    notFound();
  }

  return <CategoryListing slugPath={slug} searchParams={sp} />;
}
