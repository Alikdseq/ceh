import { CatalogGridSkeleton } from "@/components/ui/skeleton";

export default function CategoryLoading() {
  return (
    <div className="section-py container-page">
      <div className="mb-6 h-4 w-48 animate-pulse rounded bg-muted" />
      <div className="mb-8 h-10 w-2/3 max-w-md animate-pulse rounded bg-muted" />
      <CatalogGridSkeleton count={6} />
    </div>
  );
}
