"use client";

import { useCallback, useEffect, useId, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Loader2, Search } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { getSearchSuggestions, type SearchSuggestion } from "@/lib/api/search";
import { highlightMatch } from "@/lib/search-highlight";
import { cn } from "@/lib/utils";

interface SearchAutocompleteProps {
  className?: string;
  placeholder?: string;
  /** Light theme for mobile sheet / light backgrounds */
  variant?: "header" | "default";
  /** inline = button inside field (header bar); aside = button next to field (mobile menu) */
  submitLayout?: "inline" | "aside";
}

function useDebouncedValue<T>(value: T, delayMs: number): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const timer = window.setTimeout(() => setDebounced(value), delayMs);
    return () => window.clearTimeout(timer);
  }, [value, delayMs]);
  return debounced;
}

function suggestionHref(item: SearchSuggestion): string {
  return `/catalog/${item.category_slug}/${item.product_slug}`;
}

export function SearchAutocomplete({
  className,
  placeholder = "Поиск по артикулу или серии…",
  variant = "header",
  submitLayout = "inline",
}: SearchAutocompleteProps) {
  const router = useRouter();
  const listId = useId();
  const rootRef = useRef<HTMLDivElement>(null);
  const [query, setQuery] = useState("");
  const [suggestions, setSuggestions] = useState<SearchSuggestion[]>([]);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);
  const debouncedQuery = useDebouncedValue(query, 300);

  const fetchSuggestions = useCallback(async (q: string) => {
    if (q.trim().length < 2) {
      setSuggestions([]);
      setLoading(false);
      return;
    }
    setLoading(true);
    try {
      const data = await getSearchSuggestions(q.trim());
      setSuggestions(data.suggestions);
      setOpen(true);
      setActiveIndex(-1);
    } catch {
      setSuggestions([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void fetchSuggestions(debouncedQuery);
  }, [debouncedQuery, fetchSuggestions]);

  useEffect(() => {
    function onPointerDown(e: MouseEvent) {
      if (!rootRef.current?.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("pointerdown", onPointerDown);
    return () => document.removeEventListener("pointerdown", onPointerDown);
  }, []);

  function goToSearch(q: string) {
    const trimmed = q.trim();
    if (!trimmed) return;
    setOpen(false);
    router.push(`/search?q=${encodeURIComponent(trimmed)}`);
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    goToSearch(query);
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (!open || !suggestions.length) {
      if (e.key === "Enter") goToSearch(query);
      return;
    }
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setActiveIndex((i) => (i + 1) % suggestions.length);
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActiveIndex((i) => (i <= 0 ? suggestions.length - 1 : i - 1));
    } else if (e.key === "Enter" && activeIndex >= 0) {
      e.preventDefault();
      router.push(suggestionHref(suggestions[activeIndex]));
      setOpen(false);
    } else if (e.key === "Escape") {
      setOpen(false);
    }
  }

  const isHeader = variant === "header";
  const submitAside = submitLayout === "aside";

  return (
    <div ref={rootRef} className={cn("relative", className)}>
      <form
        onSubmit={handleSubmit}
        role="search"
        className={cn(submitAside && "flex items-stretch gap-2")}
      >
        <div className={cn("relative flex min-w-0 flex-1 items-center", submitAside && "flex-1")}>
          <Search
            className={cn(
              "pointer-events-none absolute left-3 h-4 w-4",
              isHeader ? "text-white/70" : "text-muted-foreground",
            )}
            aria-hidden
          />
          <Input
            type="search"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              if (e.target.value.trim().length >= 2) setOpen(true);
            }}
            onFocus={() => {
              if (suggestions.length) setOpen(true);
            }}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            role="combobox"
            aria-expanded={open && suggestions.length > 0}
            aria-controls={listId}
            aria-autocomplete="list"
            aria-label="Поиск по каталогу"
            autoComplete="off"
            className={cn(
              "h-10 w-full min-w-0 pl-9",
              submitAside ? "pr-3" : "pr-10",
              !submitAside && "md:pr-3",
              isHeader
                ? "border-white/20 bg-white/10 text-white placeholder:text-white/60 focus-visible:bg-white focus-visible:text-foreground focus-visible:placeholder:text-muted-foreground"
                : "md:w-full",
            )}
          />
          {loading && (
            <Loader2
              className={cn(
                "absolute right-3 h-4 w-4 animate-spin",
                isHeader ? "text-white/70" : "text-muted-foreground",
                !submitAside && "md:hidden",
              )}
              aria-hidden
            />
          )}
          {!submitAside && (
            <Button
              type="submit"
              size="sm"
              variant="ghost"
              className={cn(
                "absolute right-1 h-7 md:hidden",
                isHeader && "text-white hover:bg-white/20 hover:text-white",
              )}
            >
              Найти
            </Button>
          )}
        </div>
        {submitAside && (
          <Button type="submit" size="sm" variant="default" className="h-10 shrink-0 px-4">
            Найти
          </Button>
        )}
      </form>

      {open && debouncedQuery.trim().length >= 2 && (
        <ul
          id={listId}
          role="listbox"
          className="absolute left-0 right-0 top-full z-50 mt-1 max-h-80 overflow-auto rounded-md border bg-popover py-1 text-popover-foreground shadow-lg"
        >
          {suggestions.length === 0 && !loading && (
            <li className="px-3 py-2 text-sm text-muted-foreground">Ничего не найдено</li>
          )}
          {suggestions.map((item, index) => (
            <li key={`${item.product_slug}-${item.sku}`} role="option" aria-selected={index === activeIndex}>
              <Link
                href={suggestionHref(item)}
                className={cn(
                  "block px-3 py-2.5 text-sm transition-colors hover:bg-muted",
                  index === activeIndex && "bg-muted",
                )}
                onClick={() => setOpen(false)}
              >
                <span className="font-medium">{highlightMatch(item.sku, debouncedQuery)}</span>
                <span className="mx-1.5 text-muted-foreground">·</span>
                <span>{highlightMatch(item.name, debouncedQuery)}</span>
                <span className="mt-0.5 block text-xs text-muted-foreground">{item.category_name}</span>
              </Link>
            </li>
          ))}
          {suggestions.length > 0 && (
            <li className="border-t px-3 py-2">
              <button
                type="button"
                className="text-sm font-medium text-primary hover:underline"
                onClick={() => goToSearch(query)}
              >
                Все результаты по «{query.trim()}»
              </button>
            </li>
          )}
        </ul>
      )}
    </div>
  );
}
