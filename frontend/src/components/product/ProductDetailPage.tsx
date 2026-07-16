import { Suspense } from "react";

import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { Skeleton } from "@/components/ui/skeleton";
import { ProductConfigurator, ProductStickyBar } from "@/components/product/ProductConfigurator";
import { ProductFAQ, ProductRelated } from "@/components/product/ProductRelated";
import { ProductGallery } from "@/components/product/ProductGallery";
import { ProductTabs } from "@/components/product/ProductTabs";
import { getCategories, getFAQ } from "@/lib/api";
import { buildCategoryBreadcrumbs, getCategoryPathSlugs } from "@/lib/categories";
import { AntiCounterfeitBlock } from "@/components/content/AntiCounterfeitBlock";
import { JsonLd } from "@/components/seo/JsonLd";
import { buildProductSchema } from "@/lib/schema";
import type { ProductGroupDetail } from "@/lib/types";

interface ProductDetailPageProps {
  product: ProductGroupDetail;
}

export async function ProductDetailPage({ product }: ProductDetailPageProps) {
  const [categories, faq] = await Promise.all([
    getCategories(),
    getFAQ(5),
  ]);

  const catPath = product.category_path?.length
    ? product.category_path
    : getCategoryPathSlugs(categories, product.category_slug);
  const breadcrumbs = [
    ...buildCategoryBreadcrumbs(categories, catPath),
    { label: product.name },
  ];

  const basePath = `/catalog/${[...catPath, product.slug].join("/")}`;
  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000";

  const defaultVariant =
    product.variants.find((v) => v.is_default) ?? product.variants[0];

  const schemaBreadcrumbs = [
    { name: "Главная", url: siteUrl },
    { name: "Каталог", url: `${siteUrl}/catalog` },
    ...buildCategoryBreadcrumbs(categories, catPath)
      .slice(1)
      .map((b) => ({ name: b.label, url: `${siteUrl}${b.href ?? ""}` })),
    { name: product.name, url: `${siteUrl}${basePath}` },
  ];

  const pathMap = (slug: string) => getCategoryPathSlugs(categories, slug);

  return (
    <>
      <JsonLd
        data={buildProductSchema(product, defaultVariant ?? null, schemaBreadcrumbs, siteUrl)}
      />
      <div className="section-py pb-24 md:pb-16">
        <div className="container-page min-w-0">
          <Breadcrumbs items={breadcrumbs} className="mb-6" />
          <div className="grid min-w-0 gap-10 lg:grid-cols-2">
            <div className="min-w-0">
              <ProductGallery
                images={product.images}
                name={product.name}
                product={{
                  name: product.name,
                  slug: product.slug,
                  series_code: product.series_code,
                  product_type: product.product_type,
                  sku_code: defaultVariant?.sku_code,
                  execution: defaultVariant?.execution,
                  coil_voltage_v: defaultVariant?.coil_voltage_v,
                  image_rotation: product.image_rotation,
                }}
              />
            </div>
            <div className="min-w-0">
              <Suspense fallback={<Skeleton className="h-96 w-full" />}>
                <ProductConfigurator product={product} basePath={basePath} />
              </Suspense>
            </div>
          </div>
          <ProductTabs product={product} />
          <ProductRelated
            related={product.related}
            categoryPathMap={pathMap}
          />
          <ProductFAQ items={faq} />
          <AntiCounterfeitBlock className="mt-10" compact />
        </div>
      </div>
      <ProductStickyBar product={product} selected={defaultVariant} />
    </>
  );
}
