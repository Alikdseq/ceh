import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { ProductCard } from "@/components/catalog/ProductCard";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { Button } from "@/components/ui/button";
import { getDeliveryCity, getFeaturedProducts } from "@/lib/api";
import { buildPageMetadata } from "@/lib/seo";

interface DeliveryCityPageProps {
  params: Promise<{ citySlug: string }>;
}

export async function generateMetadata({ params }: DeliveryCityPageProps): Promise<Metadata> {
  const { citySlug } = await params;
  const city = await getDeliveryCity(citySlug);
  if (!city) return {};
  const title =
    city.meta_title || `Контакторы с доставкой в ${city.name} — завод Электроконтактор`;
  const description =
    city.meta_description ||
    `Прямые поставки контакторов КТ, КТП, КТЭ в ${city.name}. Цены производителя, паспорта и чертежи на сайте.`;
  return buildPageMetadata({
    title,
    description,
    path: `/delivery/${citySlug}/`,
    noindex: city.is_indexable === false,
  });
}

export default async function DeliveryCityPage({ params }: DeliveryCityPageProps) {
  const { citySlug } = await params;
  const city = await getDeliveryCity(citySlug);
  if (!city) notFound();

  const products = await getFeaturedProducts(4);

  return (
    <div className="section-py">
      <div className="container-page">
        <Breadcrumbs
          items={[
            { label: "Главная", href: "/" },
            { label: "Доставка", href: "/delivery/" },
            { label: city.name },
          ]}
          className="mb-6"
        />
        <h1 className="font-display text-3xl font-bold md:text-4xl">
          Контакторы с доставкой в {city.name}
        </h1>
        {city.region_name && (
          <p className="mt-2 text-muted-foreground">{city.region_name}</p>
        )}
        {city.intro_html ? (
          <div
            className="prose prose-slate mt-6 max-w-none"
            dangerouslySetInnerHTML={{ __html: city.intro_html }}
          />
        ) : (
          <p className="mt-6 max-w-3xl text-muted-foreground">
            АО «Электроконтактор» поставляет контакторы серий КТ, КТП и КТЭ напрямую с завода.
            Оформите заявку на коммерческое предложение с указанием адреса доставки в {city.name}.
          </p>
        )}
        <div className="mt-8 flex flex-wrap gap-3">
          <Button asChild>
            <Link href="/cart/">Запросить КП</Link>
          </Button>
          <Button asChild variant="outline">
            <Link href="/catalog/">Каталог продукции</Link>
          </Button>
        </div>
        {products.length > 0 && (
          <section className="mt-12">
            <h2 className="font-display text-xl font-semibold">Популярные модели</h2>
            <ul className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {products.map((product) => (
                <li key={product.id}>
                  <ProductCard
                    product={product}
                    categoryPath={
                      product.category_path?.length ? product.category_path : [product.category_slug]
                    }
                  />
                </li>
              ))}
            </ul>
          </section>
        )}
      </div>
    </div>
  );
}
