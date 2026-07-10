import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { CatalogFilters, CatalogFiltersMobile } from "@/components/catalog/CatalogFilters";
import { CatalogPagination, CatalogToolbar } from "@/components/catalog/CatalogToolbar";
import { ProductCard } from "@/components/catalog/ProductCard";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { Button } from "@/components/ui/button";
import { getCategories, getProducts } from "@/lib/api";
import {
  buildCategoryBreadcrumbs,
  findCategoryByPath,
  getCategoryPathSlugs,
} from "@/lib/categories";
import {
  parseCatalogParams,
  shouldNoindexCatalogParams,
  toApiParams,
} from "@/lib/catalog-params";
import { hasCatalogFilters } from "@/lib/catalog-filter-config";
import { buildCategoryMetadata } from "@/lib/seo";
import type { PaginatedResponse, ProductGroup } from "@/lib/types";

interface CategoryListingProps {
  slugPath: string[];
  searchParams: Record<string, string | string[] | undefined>;
}

export async function generateCategoryMetadata(
  slugPath: string[],
  searchParams: Record<string, string | string[] | undefined>,
): Promise<Metadata> {
  const categories = await getCategories();
  const category = findCategoryByPath(categories, slugPath);
  if (!category) return {};
  const params = parseCatalogParams(searchParams);
  const noindexParams = shouldNoindexCatalogParams(params);
  return buildCategoryMetadata(category, slugPath, { noindexParams });
}

export async function CategoryListing({ slugPath, searchParams }: CategoryListingProps) {
  const categories = await getCategories();
  const category = findCategoryByPath(categories, slugPath);
  if (!category) notFound();

  const params = parseCatalogParams(searchParams);
  const basePath = `/catalog/${slugPath.join("/")}`;

  let products: PaginatedResponse<ProductGroup> = {
    count: 0,
    results: [],
    next: null,
    previous: null,
  };
  try {
    products = await getProducts(toApiParams(params, category.slug));
  } catch {
    /* API unavailable */
  }

  const breadcrumbs = buildCategoryBreadcrumbs(categories, slugPath);
  const showFilters = hasCatalogFilters(slugPath);

  return (
    <div className="section-py">
      <div className="container-page">
        <Breadcrumbs items={breadcrumbs} className="mb-6" />
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h1 className="font-display text-3xl font-bold md:text-4xl">
              {category.h1 || category.name}
            </h1>
            {category.description && (
              <p className="mt-3 max-w-3xl text-muted-foreground">{category.description}</p>
            )}
          </div>
          <CatalogFiltersMobile basePath={basePath} params={params} categorySlugPath={slugPath} />
        </div>

        {category.children && category.children.length > 0 && (
          <div className="mt-6 flex flex-wrap gap-2">
            {category.children.map((child) => (
              <Button key={child.id} asChild variant="outline" size="sm">
                <Link href={`${basePath}/${child.slug}`}>{child.name}</Link>
              </Button>
            ))}
          </div>
        )}

        <div
          className={
            showFilters ? "mt-8 grid gap-8 lg:grid-cols-[240px_1fr]" : "mt-8"
          }
        >
          <CatalogFilters
            basePath={basePath}
            params={params}
            categorySlugPath={slugPath}
          />

          <div>
            <CatalogToolbar basePath={basePath} params={params} total={products.count} />

            {products.results.length === 0 ? (
              <div className="py-16 text-center">
                <p className="text-lg font-medium">По вашему запросу ничего не найдено</p>
                <p className="mt-2 text-muted-foreground">
                  Попробуйте изменить фильтры или сбросить их
                </p>
                <Button asChild className="mt-6" variant="outline">
                  <Link href={basePath}>Сбросить фильтры</Link>
                </Button>
              </div>
            ) : (
              <div
                className={
                  params.view === "list"
                    ? "mt-6 flex flex-col gap-3"
                    : "mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-3"
                }
              >
                {products.results.map((product, index) => (
                  <ProductCard
                    key={product.id}
                    product={product}
                    categoryPath={getCategoryPathSlugs(categories, product.category_slug)}
                    view={params.view ?? "grid"}
                    priority={index < 6}
                  />
                ))}
              </div>
            )}

            <CatalogPagination basePath={basePath} params={params} total={products.count} />
          </div>
        </div>
      </div>
    </div>
  );
}
