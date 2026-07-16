import Link from "next/link";
import Image from "next/image";
import type { LucideIcon } from "lucide-react";
import { ArrowRight } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import type { Category } from "@/lib/types";
import { getCategoryMeta } from "@/lib/catalog-meta";
import { cn, publicAssetSrc } from "@/lib/utils";

interface CategoryCardProps {
  category: Category;
}

export function CategoryCard({ category }: CategoryCardProps) {
  const meta = getCategoryMeta(category.slug);
  const Icon = meta.icon as LucideIcon;
  const rotateCategoryImage =
    category.slug === "kontaktory-kt" || category.slug === "kontaktory-ktp";

  return (
    <Link href={`/catalog/${category.slug}`}>
      <Card className="group h-full overflow-hidden transition hover:border-primary hover:shadow-md">
        <CardContent className="flex h-full flex-col p-7 md:p-8">
          <div
            className={`mb-4 flex h-24 w-24 shrink-0 items-center justify-center overflow-hidden rounded-xl md:h-28 md:w-28 ${meta.image ? "bg-white p-1.5" : meta.color}`}
          >
            {meta.image ? (
              <Image
                src={publicAssetSrc(meta.image)}
                alt=""
                width={112}
                height={112}
                className={cn("h-full w-full object-contain", rotateCategoryImage && "-rotate-90")}
                unoptimized
              />
            ) : (
              <Icon className="h-10 w-10 md:h-12 md:w-12" aria-hidden />
            )}
          </div>
          <h2 className="font-display text-xl font-semibold leading-snug md:text-2xl group-hover:text-primary">
            {category.name}
          </h2>
          <p className="mt-2 flex-1 text-sm text-muted-foreground">
            {category.description || meta.description}
          </p>
          <div className="mt-4 flex items-center justify-between">
            {category.product_count !== undefined && category.product_count > 0 && (
              <Badge variant="secondary">{category.product_count} поз.</Badge>
            )}
            <span className="flex items-center text-sm font-medium text-primary opacity-0 transition group-hover:opacity-100">
              Смотреть
              <ArrowRight className="ml-1 h-4 w-4" />
            </span>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
