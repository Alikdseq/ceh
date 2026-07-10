import { CatalogGridSkeleton } from "@/components/ui/skeleton";
import { Skeleton } from "@/components/ui/skeleton";

export default function CatalogSegmentLoading() {
  return (
    <div className="section-py container-page">
      <div className="grid gap-10 lg:grid-cols-2">
        <Skeleton className="aspect-square w-full" />
        <div className="space-y-4">
          <Skeleton className="h-10 w-3/4" />
          <Skeleton className="h-6 w-1/2" />
          <Skeleton className="h-32 w-full" />
        </div>
      </div>
      <div className="mt-12">
        <CatalogGridSkeleton count={4} />
      </div>
    </div>
  );
}
