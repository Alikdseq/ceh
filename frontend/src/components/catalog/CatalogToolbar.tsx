"use client";

import { useState, useTransition, type ReactNode } from "react";
import { useRouter } from "next/navigation";
import { Grid3X3, LayoutList } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  PAGE_SIZE_OPTIONS,
  SORT_OPTIONS,
  type CatalogSearchParams,
  buildCatalogQuery,
  buildSearchQuery,
} from "@/lib/catalog-params";
import { cn } from "@/lib/utils";

interface CatalogToolbarProps {
  basePath: string;
  params: CatalogSearchParams;
  total: number;
  mode?: "catalog" | "search";
  searchQuery?: string;
  onParamsChange?: (patch: Partial<CatalogSearchParams>) => void;
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

function ToolbarSelect({
  value,
  onValueChange,
  triggerClassName,
  children,
}: {
  value: string;
  onValueChange: (value: string) => void;
  triggerClassName?: string;
  children: ReactNode;
}) {
  const [open, setOpen] = useState(false);

  function handleValueChange(next: string) {
    setOpen(false);
    queueMicrotask(() => onValueChange(next));
  }

  return (
    <Select open={open} onOpenChange={setOpen} value={value} onValueChange={handleValueChange}>
      <SelectTrigger className={triggerClassName}>
        <SelectValue />
      </SelectTrigger>
      <SelectContent>{children}</SelectContent>
    </Select>
  );
}

export function CatalogToolbar({
  basePath,
  params,
  total,
  mode = "catalog",
  searchQuery,
  onParamsChange,
}: CatalogToolbarProps) {
  const router = useRouter();
  const [isPending, startTransition] = useTransition();

  function navigate(patch: Partial<CatalogSearchParams>) {
    if (onParamsChange) {
      onParamsChange(patch);
      return;
    }

    const href = `${basePath}${buildQueryString(mode, params, patch, searchQuery)}`;
    startTransition(() => {
      router.push(href, { scroll: false });
    });
  }

  return (
    <div
      className={cn(
        "flex flex-wrap items-center justify-between gap-3 border-b pb-4 transition-opacity duration-200",
        isPending && "opacity-70",
      )}
    >
      <p className="text-sm text-muted-foreground">
        Найдено: <span className="font-medium text-foreground">{total}</span>
      </p>
      <div className="flex flex-wrap items-center gap-2">
        <ToolbarSelect
          value={params.ordering ?? "sort_order"}
          onValueChange={(v) =>
            navigate({ ordering: v === "sort_order" ? undefined : v, page: "1" })
          }
          triggerClassName="w-[180px]"
        >
          {SORT_OPTIONS.map((o) => (
            <SelectItem key={o.value} value={o.value}>
              {o.label}
            </SelectItem>
          ))}
        </ToolbarSelect>

        <ToolbarSelect
          value={params.page_size ?? "24"}
          onValueChange={(v) =>
            navigate({ page_size: v === "24" ? undefined : v, page: "1" })
          }
          triggerClassName="w-[100px]"
        >
          {PAGE_SIZE_OPTIONS.map((n) => (
            <SelectItem key={n} value={String(n)}>
              {n}
            </SelectItem>
          ))}
        </ToolbarSelect>

        <div className="flex rounded-md border p-0.5">
          <Button
            type="button"
            variant={params.view !== "list" ? "secondary" : "ghost"}
            size="icon"
            className="h-8 w-8"
            aria-label="Сетка"
            onClick={() => navigate({ view: "grid" })}
          >
            <Grid3X3 className="h-4 w-4" />
          </Button>
          <Button
            type="button"
            variant={params.view === "list" ? "secondary" : "ghost"}
            size="icon"
            className="h-8 w-8"
            aria-label="Список"
            onClick={() => navigate({ view: "list" })}
          >
            <LayoutList className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}

export function CatalogPagination({
  basePath,
  params,
  total,
  mode = "catalog",
  searchQuery,
  onPageChange,
}: CatalogToolbarProps & { onPageChange?: (page: number) => void }) {
  const router = useRouter();
  const [isPending, startTransition] = useTransition();
  const pageSize = Number(params.page_size ?? 24);
  const page = Number(params.page ?? 1);
  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  if (totalPages <= 1) return null;

  function goTo(p: number) {
    if (onPageChange) {
      onPageChange(p);
      return;
    }

    const href = `${basePath}${buildQueryString(
      mode,
      params,
      { page: p === 1 ? undefined : String(p) },
      searchQuery,
    )}`;
    startTransition(() => {
      router.push(href, { scroll: true });
    });
  }

  return (
    <nav
      className={cn(
        "mt-8 flex justify-center gap-2 transition-opacity duration-200",
        isPending && "opacity-70",
      )}
      aria-label="Пагинация"
    >
      <Button variant="outline" size="sm" disabled={page <= 1 || isPending} onClick={() => goTo(page - 1)}>
        Назад
      </Button>
      <span className="flex items-center px-3 text-sm text-muted-foreground">
        {page} / {totalPages}
      </span>
      <Button
        variant="outline"
        size="sm"
        disabled={page >= totalPages || isPending}
        onClick={() => goTo(page + 1)}
      >
        Вперёд
      </Button>
    </nav>
  );
}
