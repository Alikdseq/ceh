"use client";

import { useRouter } from "next/navigation";
import { SlidersHorizontal } from "lucide-react";

import { FilterDropdown } from "@/components/catalog/FilterDropdown";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import {
  getAvailableFilters,
  hasCatalogFilters,
  type CatalogFilterKey,
} from "@/lib/catalog-filter-config";
import {
  COIL_OPTIONS,
  CURRENT_OPTIONS,
  EXECUTION_OPTIONS,
  POLES_OPTIONS,
  PRODUCT_TYPE_OPTIONS,
  SERIES_OPTIONS,
  type CatalogSearchParams,
  buildCatalogQuery,
  buildSearchQuery,
} from "@/lib/catalog-params";
import { cn } from "@/lib/utils";

interface CatalogFiltersProps {
  basePath: string;
  params: CatalogSearchParams;
  categorySlugPath?: string[];
  className?: string;
  mobile?: boolean;
  mode?: "catalog" | "search";
  searchQuery?: string;
  resetPath?: string;
}

function buildQueryString(
  mode: "catalog" | "search",
  params: CatalogSearchParams,
  patch: Partial<CatalogSearchParams>,
  searchQuery?: string,
): string {
  if (mode === "search" && searchQuery) {
    return buildSearchQuery(params, searchQuery, patch);
  }
  return buildCatalogQuery(params, patch);
}

function firstOrAll(values: string[] | undefined): string {
  return values?.[0] ?? "all";
}

function FilterFields({
  params,
  availableFilters,
  dropdownMode,
  onChange,
}: {
  params: CatalogSearchParams;
  availableFilters: CatalogFilterKey[];
  dropdownMode: "hover" | "tap";
  onChange: (patch: Partial<CatalogSearchParams>) => void;
}) {
  const show = (key: CatalogFilterKey) => availableFilters.includes(key);

  return (
    <div className="space-y-5">
      {show("current") && (
        <FilterDropdown
          mode={dropdownMode}
          label="Номинальный ток, А"
          value={firstOrAll(params.current)}
          placeholder="Любой"
          options={[
            { value: "all", label: "Любой" },
            ...CURRENT_OPTIONS.map((v) => ({ value: String(v), label: `${v} А` })),
          ]}
          onChange={(v) =>
            onChange({ current: v === "all" ? undefined : [v], page: "1" })
          }
        />
      )}

      {show("coil") && (
        <FilterDropdown
          mode={dropdownMode}
          label="Напряжение катушки, В"
          value={firstOrAll(params.coil)}
          placeholder="Любое"
          options={[
            { value: "all", label: "Любое" },
            ...COIL_OPTIONS.map((v) => ({ value: String(v), label: `${v} В` })),
          ]}
          onChange={(v) => onChange({ coil: v === "all" ? undefined : [v], page: "1" })}
        />
      )}

      {show("poles") && (
        <FilterDropdown
          mode={dropdownMode}
          label="Число полюсов"
          value={firstOrAll(params.poles)}
          placeholder="Любое"
          options={[
            { value: "all", label: "Любое" },
            ...POLES_OPTIONS.map((v) => ({ value: String(v), label: String(v) })),
          ]}
          onChange={(v) => onChange({ poles: v === "all" ? undefined : [v], page: "1" })}
        />
      )}

      {show("execution") && (
        <FilterDropdown
          mode={dropdownMode}
          label="Исполнение"
          value={firstOrAll(params.execution)}
          placeholder="Любое"
          options={[
            { value: "all", label: "Любое" },
            ...EXECUTION_OPTIONS.map((o) => ({ value: o.value, label: o.label })),
          ]}
          onChange={(v) =>
            onChange({ execution: v === "all" ? undefined : [v], page: "1" })
          }
        />
      )}

      {show("product_type") && (
        <FilterDropdown
          mode={dropdownMode}
          label="Тип"
          value={firstOrAll(params.product_type)}
          placeholder="Любой"
          options={[
            { value: "all", label: "Любой" },
            ...PRODUCT_TYPE_OPTIONS.map((o) => ({ value: o.value, label: o.label })),
          ]}
          onChange={(v) =>
            onChange({ product_type: v === "all" ? undefined : [v], page: "1" })
          }
        />
      )}

      {show("series") && (
        <FilterDropdown
          mode={dropdownMode}
          label="Серия"
          value={firstOrAll(params.series)}
          placeholder="Любая"
          options={[
            { value: "all", label: "Любая" },
            ...SERIES_OPTIONS.map((v) => ({ value: v, label: v })),
          ]}
          onChange={(v) => onChange({ series: v === "all" ? undefined : [v], page: "1" })}
        />
      )}
    </div>
  );
}

export function CatalogFilters({
  basePath,
  params,
  categorySlugPath = [],
  className,
  mobile,
  mode = "catalog",
  searchQuery,
  resetPath = basePath,
}: CatalogFiltersProps) {
  const router = useRouter();
  const availableFilters =
    mode === "search"
      ? (["current", "coil", "poles", "execution", "product_type", "series"] as CatalogFilterKey[])
      : getAvailableFilters(categorySlugPath);

  if (mode === "catalog" && !hasCatalogFilters(categorySlugPath)) {
    return null;
  }

  function navigate(patch: Partial<CatalogSearchParams>) {
    router.push(`${basePath}${buildQueryString(mode, params, patch, searchQuery)}`, {
      scroll: false,
    });
  }

  function reset() {
    router.push(resetPath, { scroll: false });
  }

  const fields = (
    <FilterFields
      params={params}
      availableFilters={availableFilters}
      dropdownMode={mobile ? "tap" : "hover"}
      onChange={navigate}
    />
  );

  if (mobile) {
    if (mode === "catalog" && !hasCatalogFilters(categorySlugPath)) {
      return null;
    }

    return (
      <Sheet>
        <SheetTrigger asChild>
          <Button variant="outline" size="sm" className="gap-2 lg:hidden">
            <SlidersHorizontal className="h-4 w-4" />
            Фильтры
          </Button>
        </SheetTrigger>
        <SheetContent side="bottom" className="max-h-[85vh] overflow-y-auto">
          <SheetHeader>
            <SheetTitle>Фильтры</SheetTitle>
          </SheetHeader>
          <div className="mt-6">{fields}</div>
          <Button variant="outline" className="mt-6 w-full" onClick={reset}>
            Сбросить фильтры
          </Button>
        </SheetContent>
      </Sheet>
    );
  }

  return (
    <aside className={cn("hidden space-y-4 lg:block", className)}>
      <div className="flex items-center justify-between">
        <h2 className="font-display font-semibold">Фильтры</h2>
        <Button variant="link" size="sm" className="h-auto p-0" onClick={reset}>
          Сбросить
        </Button>
      </div>
      {fields}
    </aside>
  );
}

export function CatalogFiltersMobile(props: CatalogFiltersProps) {
  return <CatalogFilters {...props} mobile />;
}
