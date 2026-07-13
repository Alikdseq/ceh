"use client";

import { useCallback, useEffect, useRef, useState, useTransition } from "react";

import { CatalogPagination, CatalogToolbar } from "@/components/catalog/CatalogToolbar";
import { ProductCard } from "@/components/catalog/ProductCard";
import { SmartCatalogFilter } from "@/components/catalog/SmartCatalogFilter";
import { Button } from "@/components/ui/button";
import { CatalogGridSkeleton, Skeleton } from "@/components/ui/skeleton";
import { cn, PRODUCT_IMAGE_ASPECT_CLASS } from "@/lib/utils";
import {
  fetchCatalogFilterClient,
  type CatalogFilterResponse,
  type CatalogFiltersMeta,
} from "@/lib/api/catalog-filter";
import { getCategoryPathSlugs } from "@/lib/categories";
import {
  buildCatalogQuery,
  loadFiltersFromSession,
  saveFiltersToSession,
  toFilterApiParams,
  type CatalogSearchParams,
} from "@/lib/catalog-params";
import type { Category, ProductGroup } from "@/lib/types";

const EMPTY_META: CatalogFiltersMeta = {
  category_type: {},
  product_type: {},
  current_rating: { min: null, max: null, available: [], counts: {} },
  coil_voltage: { min: null, max: null, available: [], counts: {} },
  execution: {},
  poles: {},
  series: {},
  application: {},
  documentation: {},
};

interface CatalogListingClientProps {
  basePath: string;
  categorySlug: string;
  categories: Category[];
  initialParams: CatalogSearchParams;
  initialData: CatalogFilterResponse;
}

export function CatalogListingClient({
  basePath,
  categorySlug,
  categories,
  initialParams,
  initialData,
}: CatalogListingClientProps) {
  const [params, setParams] = useState<CatalogSearchParams>(initialParams);
  const [products, setProducts] = useState<ProductGroup[]>(initialData.results);
  const [total, setTotal] = useState(initialData.count);
  const [meta, setMeta] = useState<CatalogFiltersMeta>(initialData.filters_meta ?? EMPTY_META);
  const [isPending, startTransition] = useTransition();
  const lastRequest = useRef<string>("");

  const fetchFiltered = useCallback(
    async (nextParams: CatalogSearchParams) => {
      const apiParams = toFilterApiParams(nextParams, categorySlug);
      const signature = JSON.stringify(apiParams);
      if (signature === lastRequest.current) return;
      lastRequest.current = signature;

      const data = await fetchCatalogFilterClient(apiParams);
      if (process.env.NODE_ENV === "development") {
        console.log("Products found:", data.count);
      }
      setProducts(data.results);
      setTotal(data.count);
      setMeta(data.filters_meta ?? EMPTY_META);
      setParams(nextParams);
      const qs = buildCatalogQuery(nextParams);
      window.history.pushState({}, "", `${basePath}${qs}`);
      saveFiltersToSession(basePath, nextParams);
    },
    [basePath, categorySlug],
  );

  useEffect(() => {
    const stored = loadFiltersFromSession(basePath);
    if (stored && JSON.stringify(stored) !== JSON.stringify(initialParams)) {
      startTransition(() => {
        void fetchFiltered(stored);
      });
    }
  }, [basePath, fetchFiltered, initialParams]);

  function handleApply(next: CatalogSearchParams) {
    startTransition(() => {
      void fetchFiltered(next);
    });
  }

  function handleReset() {
    const cleared: CatalogSearchParams = { view: params.view ?? "grid" };
    lastRequest.current = "";
    startTransition(() => {
      void fetchFiltered(cleared);
    });
  }

  function handleToolbarChange(patch: Partial<CatalogSearchParams>) {
    startTransition(() => {
      void fetchFiltered({ ...params, ...patch });
    });
  }

  return (
    <>
      <div className="mt-8 flex justify-end lg:hidden">
        <SmartCatalogFilter
          params={params}
          meta={meta}
          onApply={handleApply}
          onReset={handleReset}
          loading={isPending}
          mobile
        />
      </div>

      <div className="mt-4 grid gap-8 lg:mt-8 lg:grid-cols-[280px_1fr]">
      <SmartCatalogFilter
        params={params}
        meta={meta}
        onApply={handleApply}
        onReset={handleReset}
        loading={isPending}
        className="w-full"
      />

      <div>
        <CatalogToolbar
          basePath={basePath}
          params={params}
          total={total}
          onParamsChange={handleToolbarChange}
        />

        <div
          className="transition-opacity duration-300"
          style={{ opacity: isPending ? 0.55 : 1 }}
        >
          {isPending && products.length === 0 ? (
            <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
              {Array.from({ length: 6 }).map((_, i) => (
                <Skeleton key={i} className={cn("w-full rounded-lg", PRODUCT_IMAGE_ASPECT_CLASS)} />
              ))}
            </div>
          ) : products.length === 0 ? (
            <div className="py-16 text-center">
              <p className="text-lg font-medium">По вашему запросу ничего не найдено</p>
              <p className="mt-2 text-muted-foreground">
                Попробуйте изменить условия поиска или сбросить фильтры
              </p>
              <Button type="button" variant="outline" className="mt-6" onClick={handleReset}>
                Сбросить фильтры
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
              {products.map((product, index) => (
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
        </div>

        <CatalogPagination
          basePath={basePath}
          params={params}
          total={total}
          onPageChange={(page) => handleToolbarChange({ page: String(page) })}
        />
      </div>
      </div>
    </>
  );
}
