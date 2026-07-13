import { CatalogGridSkeleton, Skeleton } from "@/components/ui/skeleton";
import { PRODUCT_IMAGE_ASPECT_CLASS } from "@/lib/utils";

export default function CatalogSegmentLoading() {
  return (
    <div className="section-py container-page">
      <div className="grid gap-10 lg:grid-cols-2">
        <Skeleton className={`w-full ${PRODUCT_IMAGE_ASPECT_CLASS}`} />
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
