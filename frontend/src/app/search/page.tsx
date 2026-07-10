import type { Metadata } from "next";
import Link from "next/link";

import { CatalogFilters, CatalogFiltersMobile } from "@/components/catalog/CatalogFilters";
import { CatalogPagination, CatalogToolbar } from "@/components/catalog/CatalogToolbar";
import { ProductCard } from "@/components/catalog/ProductCard";
import { SearchAutocomplete } from "@/components/layout/SearchAutocomplete";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { getCategories, searchProducts } from "@/lib/api";
import { getCategoryPathSlugs } from "@/lib/categories";
import { parseCatalogParams, toSearchApiParams } from "@/lib/catalog-params";
import { buildSearchMetadata } from "@/lib/seo";
import type { PaginatedResponse, ProductGroup } from "@/lib/types";

interface SearchPageProps {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}

export async function generateMetadata({ searchParams }: SearchPageProps): Promise<Metadata> {
  const raw = await searchParams;
  const q = Array.isArray(raw.q) ? raw.q[0] : raw.q;
  return buildSearchMetadata(q);
}

export default async function SearchPage({ searchParams }: SearchPageProps) {
  const raw = await searchParams;
  const q = (Array.isArray(raw.q) ? raw.q[0] : raw.q)?.trim() ?? "";
  const params = parseCatalogParams(raw);
  const basePath = "/search";
  const resetPath = q ? `${basePath}?q=${encodeURIComponent(q)}` : basePath;

  let products: PaginatedResponse<ProductGroup> = {
    count: 0,
    results: [],
    next: null,
    previous: null,
  };

  const categories = await getCategories();

  if (q.length >= 2) {
    try {
      products = await searchProducts(toSearchApiParams(params, q));
    } catch {
      /* API unavailable */
    }
  }

  return (
    <div className="section-py">
      <div className="container-page">
        <Breadcrumbs
          items={[
            { label: "Главная", href: "/" },
            { label: "Поиск", href: "/search" },
          ]}
          className="mb-6"
        />

        <div className="max-w-xl">
          <h1 className="font-display text-3xl font-bold md:text-4xl">Поиск по каталогу</h1>
          <SearchAutocomplete className="mt-4 sm:hidden" variant="default" />
        </div>

        {!q && (
          <p className="mt-8 text-muted-foreground">
            Введите артикул, серию или название в строку поиска в шапке сайта.
          </p>
        )}

        {q && q.length < 2 && (
          <p className="mt-8 text-muted-foreground">Введите минимум 2 символа для поиска.</p>
        )}

        {q.length >= 2 && (
          <>
            <p className="mt-4 text-muted-foreground">
              Результаты по запросу «<span className="font-medium text-foreground">{q}</span>»
            </p>

            <div className="mt-8 flex flex-wrap items-start justify-between gap-4">
              <CatalogFiltersMobile
                basePath={basePath}
                params={params}
                mode="search"
                searchQuery={q}
                resetPath={resetPath}
              />
            </div>

            <div className="mt-6 flex flex-col gap-8 lg:flex-row">
              <CatalogFilters
                basePath={basePath}
                params={params}
                mode="search"
                searchQuery={q}
                resetPath={resetPath}
                className="w-56 shrink-0"
              />

              <div className="min-w-0 flex-1">
                <CatalogToolbar
                  basePath={basePath}
                  params={params}
                  total={products.count}
                  mode="search"
                  searchQuery={q}
                />

                {products.results.length === 0 ? (
                  <div className="mt-12 text-center">
                    <p className="text-lg text-muted-foreground">По вашему запросу ничего не найдено.</p>
                    <Link href="/catalog/" className="mt-4 inline-block text-primary hover:underline">
                      Перейти в каталог
                    </Link>
                  </div>
                ) : (
                  <>
                    <ul
                      className={
                        params.view === "list"
                          ? "mt-6 flex flex-col gap-4"
                          : "mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-3"
                      }
                    >
                      {products.results.map((product, index) => (
                        <li key={product.id}>
                          <ProductCard
                            product={product}
                            categoryPath={getCategoryPathSlugs(categories, product.category_slug)}
                            view={params.view}
                            highlightQuery={q}
                            priority={index < 6}
                          />
                        </li>
                      ))}
                    </ul>
                    <CatalogPagination
                      basePath={basePath}
                      params={params}
                      total={products.count}
                      mode="search"
                      searchQuery={q}
                    />
                  </>
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
