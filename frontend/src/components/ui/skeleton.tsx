import { cn, PRODUCT_IMAGE_ASPECT_CLASS } from "@/lib/utils";

export function Skeleton({ className }: { className?: string }) {
  return <div className={cn("animate-pulse rounded-md bg-muted", className)} aria-hidden />;
}

export function ProductCardSkeleton({ view = "grid" }: { view?: "grid" | "list" }) {
  if (view === "list") {
    return (
      <div className="flex gap-4 rounded-lg border p-4">
        <Skeleton className={cn("h-24 w-40 shrink-0", PRODUCT_IMAGE_ASPECT_CLASS)} />
        <div className="flex-1 space-y-2">
          <Skeleton className="h-5 w-2/3" />
          <Skeleton className="h-4 w-1/3" />
          <Skeleton className="h-6 w-24" />
        </div>
      </div>
    );
  }
  return (
    <div className="overflow-hidden rounded-lg border">
      <Skeleton className={cn("w-full rounded-none", PRODUCT_IMAGE_ASPECT_CLASS)} />
      <div className="space-y-2 p-4">
        <Skeleton className="h-5 w-full" />
        <Skeleton className="h-4 w-1/2" />
        <Skeleton className="h-8 w-full" />
      </div>
    </div>
  );
}

export function CatalogGridSkeleton({ count = 8, view = "grid" }: { count?: number; view?: "grid" | "list" }) {
  return (
    <div
      className={cn(
        view === "grid"
          ? "grid gap-4 sm:grid-cols-2 xl:grid-cols-3"
          : "flex flex-col gap-3",
      )}
    >
      {Array.from({ length: count }).map((_, i) => (
        <ProductCardSkeleton key={i} view={view} />
      ))}
    </div>
  );
}
