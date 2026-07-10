import Link from "next/link";
import { ArrowRight } from "lucide-react";

import { ProductCard } from "@/components/catalog/ProductCard";
import { Button } from "@/components/ui/button";
import type { ProductGroup } from "@/lib/types";

interface FeaturedProductsProps {
  products: ProductGroup[];
}

export function FeaturedProducts({ products }: FeaturedProductsProps) {
  if (products.length === 0) return null;

  return (
    <section className="section-py bg-background" aria-labelledby="featured-heading">
      <div className="container-page">
        <div className="flex items-end justify-between gap-4">
          <div>
            <h2 id="featured-heading" className="font-display text-2xl font-bold md:text-3xl">
              Хиты продаж
            </h2>
            <p className="mt-2 text-muted-foreground">Популярные позиции с завода-производителя</p>
          </div>
          <Button asChild variant="outline" className="hidden sm:inline-flex">
            <Link href="/catalog">
              Весь каталог
              <ArrowRight className="h-4 w-4" />
            </Link>
          </Button>
        </div>

        <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {products.map((product, index) => (
            <ProductCard
              key={product.id}
              product={product}
              categoryPath={product.category_path?.length ? product.category_path : [product.category_slug]}
              priority={index < 4}
            />
          ))}
        </div>
      </div>
    </section>
  );
}
