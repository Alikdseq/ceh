import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { Button } from "@/components/ui/button";
import { getCategories, getCityCategoryLanding, getDeliveryCity } from "@/lib/api";
import { getCategoryPathSlugs } from "@/lib/categories";
import { buildPageMetadata } from "@/lib/seo";

interface DeliveryCategoryPageProps {
  params: Promise<{ citySlug: string; categorySlug: string }>;
}

export async function generateMetadata({ params }: DeliveryCategoryPageProps): Promise<Metadata> {
  const { citySlug, categorySlug } = await params;
  const [city, landing] = await Promise.all([
    getDeliveryCity(citySlug),
    getCityCategoryLanding(citySlug, categorySlug),
  ]);
  if (!landing || !city) return {};
  const title =
    landing.meta_title ||
    `${landing.category_name} с доставкой в ${city.name}`;
  const description =
    landing.meta_description ||
    `Поставки ${landing.category_name.toLowerCase()} напрямую с завода.`;
  return buildPageMetadata({
    title,
    description,
    path: `/delivery/${citySlug}/${categorySlug}/`,
    noindex: landing.is_indexable === false,
  });
}

export default async function DeliveryCategoryPage({ params }: DeliveryCategoryPageProps) {
  const { citySlug, categorySlug } = await params;
  const [city, landing, categories] = await Promise.all([
    getDeliveryCity(citySlug),
    getCityCategoryLanding(citySlug, categorySlug),
    getCategories(),
  ]);

  if (!city || !landing) {
    notFound();
  }

  const categoryPath = getCategoryPathSlugs(categories, categorySlug);
  const catalogHref =
    categoryPath.length > 0
      ? `/catalog/${categoryPath.join("/")}/`
      : `/catalog/${categorySlug}/`;

  return (
    <div className="section-py">
      <div className="container-page">
        <Breadcrumbs
          items={[
            { label: "Главная", href: "/" },
            { label: "Доставка", href: "/delivery/" },
            { label: city.name, href: `/delivery/${citySlug}/` },
            { label: landing.category_name },
          ]}
          className="mb-6"
        />
        <h1 className="font-display text-3xl font-bold md:text-4xl">
          {landing.category_name} — доставка в {city.name}
        </h1>
        {landing.intro_html ? (
          <div
            className="prose prose-slate mt-6 max-w-none"
            dangerouslySetInnerHTML={{ __html: landing.intro_html }}
          />
        ) : (
          <p className="mt-6 max-w-3xl text-muted-foreground">
            Прямые поставки {landing.category_name.toLowerCase()} от производителя в {city.name}.
          </p>
        )}
        <div className="mt-8 flex flex-wrap gap-3">
          <Button asChild>
            <Link href={catalogHref}>Смотреть в каталоге</Link>
          </Button>
          <Button asChild variant="outline">
            <Link href="/cart/">Запросить КП</Link>
          </Button>
        </div>
      </div>
    </div>
  );
}
