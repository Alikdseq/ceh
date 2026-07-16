import type { Metadata } from "next";
import { redirect } from "next/navigation";

import {
  CategoryListing,
  generateCategoryMetadata,
} from "@/components/catalog/CategoryListing";
import { ProductDetailPage } from "@/components/product/ProductDetailPage";
import { tryGetProduct, getCategories } from "@/lib/api";
import { catalogPathsEqual, catalogProductPath, normalizeCatalogPath } from "@/lib/catalog-url";
import { getCategoryPathSlugs } from "@/lib/categories";
import { buildProductMetadata } from "@/lib/seo";

interface PageProps {
  params: Promise<{ categorySlug: string; productSlug: string }>;
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}

export async function generateMetadata({ params, searchParams }: PageProps): Promise<Metadata> {
  const { categorySlug, productSlug } = await params;
  const product = await tryGetProduct(productSlug);
  if (product) {
    const categories = await getCategories();
    const categoryPath =
      product.category_path?.length
        ? product.category_path
        : getCategoryPathSlugs(categories, product.category_slug);
    return buildProductMetadata(product, categoryPath);
  }
  const sp = await searchParams;
  return generateCategoryMetadata([categorySlug, productSlug], sp);
}

export default async function CatalogTwoSegmentPage({ params, searchParams }: PageProps) {
  const { categorySlug, productSlug } = await params;
  const sp = await searchParams;
  const product = await tryGetProduct(productSlug);

  if (product) {
    const categories = await getCategories();
    const catPath =
      product.category_path?.length
        ? product.category_path
        : getCategoryPathSlugs(categories, product.category_slug);
    const canonical = catalogProductPath({ slug: product.slug, category_path: catPath });
    const current = normalizeCatalogPath(`/catalog/${categorySlug}/${productSlug}`);
    if (!catalogPathsEqual(current, canonical)) {
      redirect(`${canonical}/`);
    }
    return <ProductDetailPage product={product} />;
  }

  return <CategoryListing slugPath={[categorySlug, productSlug]} searchParams={sp} />;
}
