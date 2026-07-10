"use client";

import { useEffect, useMemo, useState } from "react";
import { SlidersHorizontal } from "lucide-react";

import { DualRangeSlider } from "@/components/catalog/DualRangeSlider";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import type { CatalogFiltersMeta } from "@/lib/api/catalog-filter";
import {
  DOC_FILTER_OPTIONS,
  EXECUTION_OPTIONS,
  PRODUCT_TYPE_OPTIONS,
  type CatalogSearchParams,
  countActiveFilters,
  hasActiveFilters,
} from "@/lib/catalog-params";
import { cn, productTypeLabel } from "@/lib/utils";

interface SmartCatalogFilterProps {
  params: CatalogSearchParams;
  meta: CatalogFiltersMeta;
  onApply: (draft: CatalogSearchParams) => void;
  onReset: () => void;
  loading?: boolean;
  className?: string;
  mobile?: boolean;
}

function toggleValue(list: string[] | undefined, value: string): string[] {
  const set = new Set(list ?? []);
  if (set.has(value)) set.delete(value);
  else set.add(value);
  return [...set];
}

function toggleNumber(list: string[] | undefined, value: number): string[] {
  return toggleValue(list, String(value));
}

function FilterBody({
  draft,
  setDraft,
  meta,
}: {
  draft: CatalogSearchParams;
  setDraft: React.Dispatch<React.SetStateAction<CatalogSearchParams>>;
  meta: CatalogFiltersMeta;
}) {
  const currentMeta = meta.current_rating;
  const coilMeta = meta.coil_voltage;

  const currentRange: [number, number] = useMemo(() => {
    const minBound = currentMeta.min ?? 0;
    const maxBound = currentMeta.max ?? minBound;
    const lo = draft.current_min ? Number(draft.current_min) : minBound;
    const hi = draft.current_max ? Number(draft.current_max) : maxBound;
    return [lo, hi];
  }, [currentMeta.min, currentMeta.max, draft.current_min, draft.current_max]);

  const coilRange: [number, number] = useMemo(() => {
    const minBound = coilMeta.min ?? 0;
    const maxBound = coilMeta.max ?? minBound;
    const lo = draft.coil_min ? Number(draft.coil_min) : minBound;
    const hi = draft.coil_max ? Number(draft.coil_max) : maxBound;
    return [lo, hi];
  }, [coilMeta.min, coilMeta.max, draft.coil_min, draft.coil_max]);

  const categoryTypes = Object.entries(meta.category_type ?? {});
  const productTypes = Object.entries(meta.product_type ?? {}).filter(([, c]) => c > 0);
  const applications = Object.entries(meta.application ?? {}).filter(([, c]) => c > 0);
  const docCounts = meta.documentation ?? {};

  return (
    <Accordion
      type="multiple"
      defaultValue={["type", "specs", "docs"]}
      className="w-full"
    >
      {categoryTypes.length > 0 && (
        <AccordionItem value="type">
          <AccordionTrigger className="text-sm font-semibold">
            Тип изделия
            {draft.type?.length ? (
              <Badge variant="secondary" className="ml-2">
                {draft.type.length}
              </Badge>
            ) : null}
          </AccordionTrigger>
          <AccordionContent className="space-y-1">
            {categoryTypes.map(([slug, item]) => (
              <Checkbox
                key={slug}
                label={item.name}
                count={item.count}
                checked={draft.type?.includes(slug) ?? false}
                disabled={item.count === 0}
                onChange={() =>
                  setDraft((p) => ({ ...p, type: toggleValue(p.type, slug), page: "1" }))
                }
              />
            ))}
          </AccordionContent>
        </AccordionItem>
      )}

      {productTypes.length > 0 && (
        <AccordionItem value="product_type">
          <AccordionTrigger className="text-sm font-semibold">Серия / тип продукции</AccordionTrigger>
          <AccordionContent className="space-y-1">
            {productTypes.map(([code, count]) => (
              <Checkbox
                key={code}
                label={productTypeLabel(code)}
                count={count}
                checked={draft.product_type?.includes(code) ?? false}
                onChange={() =>
                  setDraft((p) => ({
                    ...p,
                    product_type: toggleValue(p.product_type, code),
                    page: "1",
                  }))
                }
              />
            ))}
          </AccordionContent>
        </AccordionItem>
      )}

      <AccordionItem value="specs">
        <AccordionTrigger className="text-sm font-semibold">Технические характеристики</AccordionTrigger>
        <AccordionContent className="space-y-6">
          {currentMeta.available.length > 0 && (
            <div className="space-y-3">
              <p className="text-sm font-medium">Номинальный ток (А)</p>
              {currentMeta.min !== null && currentMeta.max !== null && (
                <DualRangeSlider
                  min={currentMeta.min}
                  max={currentMeta.max}
                  value={currentRange}
                  unit="А"
                  onChange={([lo, hi]) =>
                    setDraft((p) => ({
                      ...p,
                      current_min: String(lo),
                      current_max: String(hi),
                      current: undefined,
                      page: "1",
                    }))
                  }
                />
              )}
              <div className="grid grid-cols-2 gap-x-2">
                {currentMeta.available.map((val) => (
                  <Checkbox
                    key={val}
                    label={`${val} А`}
                    count={currentMeta.counts[String(val)]}
                    checked={draft.current?.includes(String(val)) ?? false}
                    onChange={() =>
                      setDraft((p) => ({
                        ...p,
                        current: toggleNumber(p.current, val),
                        current_min: undefined,
                        current_max: undefined,
                        page: "1",
                      }))
                    }
                  />
                ))}
              </div>
            </div>
          )}

          {coilMeta.available.length > 0 && (
            <div className="space-y-3">
              <p className="text-sm font-medium">Напряжение катушки (В)</p>
              {coilMeta.min !== null && coilMeta.max !== null && (
                <DualRangeSlider
                  min={coilMeta.min}
                  max={coilMeta.max}
                  value={coilRange}
                  unit=" В"
                  onChange={([lo, hi]) =>
                    setDraft((p) => ({
                      ...p,
                      coil_min: String(lo),
                      coil_max: String(hi),
                      coil: undefined,
                      page: "1",
                    }))
                  }
                />
              )}
              <div className="grid grid-cols-2 gap-x-2">
                {coilMeta.available.map((val) => (
                  <Checkbox
                    key={val}
                    label={`${val} В`}
                    count={coilMeta.counts[String(val)]}
                    checked={draft.coil?.includes(String(val)) ?? false}
                    onChange={() =>
                      setDraft((p) => ({
                        ...p,
                        coil: toggleNumber(p.coil, val),
                        coil_min: undefined,
                        coil_max: undefined,
                        page: "1",
                      }))
                    }
                  />
                ))}
              </div>
            </div>
          )}

          {Object.keys(meta.execution ?? {}).length > 0 && (
            <div className="space-y-2">
              <p className="text-sm font-medium">Исполнение</p>
              {EXECUTION_OPTIONS.filter((o) => meta.execution[o.value]).map((o) => (
                <Checkbox
                  key={o.value}
                  label={o.label}
                  count={meta.execution[o.value]}
                  checked={draft.execution?.includes(o.value) ?? false}
                  onChange={() =>
                    setDraft((p) => ({
                      ...p,
                      execution: toggleValue(p.execution, o.value),
                      page: "1",
                    }))
                  }
                />
              ))}
            </div>
          )}

          {Object.keys(meta.poles ?? {}).length > 0 && (
            <div className="space-y-2">
              <p className="text-sm font-medium">Число полюсов</p>
              {Object.entries(meta.poles).map(([val, count]) => (
                <Checkbox
                  key={val}
                  label={val}
                  count={count}
                  checked={draft.poles?.includes(val) ?? false}
                  onChange={() =>
                    setDraft((p) => ({
                      ...p,
                      poles: toggleValue(p.poles, val),
                      page: "1",
                    }))
                  }
                />
              ))}
            </div>
          )}

          {Object.keys(meta.series ?? {}).length > 0 && (
            <div className="space-y-2">
              <p className="text-sm font-medium">Серия</p>
              {Object.entries(meta.series).map(([val, count]) => (
                <Checkbox
                  key={val}
                  label={val}
                  count={count}
                  checked={draft.series?.includes(val) ?? false}
                  onChange={() =>
                    setDraft((p) => ({
                      ...p,
                      series: toggleValue(p.series, val),
                      page: "1",
                    }))
                  }
                />
              ))}
            </div>
          )}
        </AccordionContent>
      </AccordionItem>

      {applications.length > 0 && (
        <AccordionItem value="application">
          <AccordionTrigger className="text-sm font-semibold">Применение / отрасль</AccordionTrigger>
          <AccordionContent className="space-y-1">
            {applications.map(([val, count]) => (
              <Checkbox
                key={val}
                label={val}
                count={count}
                checked={draft.application?.includes(val) ?? false}
                onChange={() =>
                  setDraft((p) => ({
                    ...p,
                    application: toggleValue(p.application, val),
                    page: "1",
                  }))
                }
              />
            ))}
          </AccordionContent>
        </AccordionItem>
      )}

      <AccordionItem value="docs">
        <AccordionTrigger className="text-sm font-semibold">Наличие документации</AccordionTrigger>
        <AccordionContent className="space-y-1">
          {DOC_FILTER_OPTIONS.map((opt) => (
            <Checkbox
              key={opt.value}
              label={opt.label}
              count={docCounts[opt.value] ?? 0}
              checked={draft.doc?.includes(opt.value) ?? false}
              disabled={(docCounts[opt.value] ?? 0) === 0}
              onChange={() =>
                setDraft((p) => ({
                  ...p,
                  doc: toggleValue(p.doc, opt.value),
                  page: "1",
                }))
              }
            />
          ))}
        </AccordionContent>
      </AccordionItem>
    </Accordion>
  );
}

export function SmartCatalogFilter({
  params,
  meta,
  onApply,
  onReset,
  loading,
  className,
  mobile,
}: SmartCatalogFilterProps) {
  const [draft, setDraft] = useState<CatalogSearchParams>(params);
  const activeCount = countActiveFilters(params);
  const draftCount = countActiveFilters(draft);

  useEffect(() => {
    setDraft(params);
  }, [params]);

  function apply() {
    if (process.env.NODE_ENV === "development") {
      console.log("Filter applied:", draft);
    }
    onApply({ ...draft, page: "1" });
  }

  function reset() {
    setDraft({ view: params.view ?? "grid" });
    onReset();
  }

  const body = <FilterBody draft={draft} setDraft={setDraft} meta={meta} />;

  const actions = (
    <div className="flex flex-col gap-2 sm:flex-row">
      <Button
        type="button"
        className="flex-1"
        onClick={apply}
        disabled={loading}
      >
        {loading ? "Загрузка…" : "Применить"}
      </Button>
      <Button
        type="button"
        variant="outline"
        className="flex-1"
        onClick={reset}
        disabled={!hasActiveFilters(params) && !hasActiveFilters(draft)}
      >
        Сбросить
      </Button>
    </div>
  );

  if (mobile) {
    return (
      <Sheet>
        <SheetTrigger asChild>
          <Button variant="outline" size="sm" className="gap-2 lg:hidden">
            <SlidersHorizontal className="h-4 w-4" />
            Фильтр
            {activeCount > 0 && (
              <Badge variant="accent" className="h-5 min-w-5 px-1.5">
                {activeCount}
              </Badge>
            )}
          </Button>
        </SheetTrigger>
        <SheetContent side="left" className="flex w-full max-w-md flex-col p-0">
          <SheetHeader className="border-b px-4 py-4">
            <SheetTitle>Фильтр по товарам</SheetTitle>
          </SheetHeader>
          <div className="flex-1 overflow-y-auto px-4 py-4">{body}</div>
          <div className="border-t px-4 py-4">{actions}</div>
        </SheetContent>
      </Sheet>
    );
  }

  return (
    <aside className={cn("hidden space-y-4 lg:block", className)}>
      <div className="flex items-center justify-between gap-2">
        <h2 className="font-display text-base font-semibold">Фильтр по товарам</h2>
        {draftCount > 0 && (
          <Badge variant="secondary">{draftCount}</Badge>
        )}
      </div>
      {body}
      <div className="sticky bottom-0 border-t bg-background pt-4">{actions}</div>
    </aside>
  );
}
