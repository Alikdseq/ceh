import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { ProductCard } from "@/components/catalog/ProductCard";
import { getPage } from "@/lib/api/content";
import { getProducts } from "@/lib/api/products";
import { getApplicationBySlug } from "@/lib/applications";
import { buildPageMetadata } from "@/lib/seo";

interface ApplicationPageProps {
  params: Promise<{ slug: string }>;
}

export async function generateMetadata({ params }: ApplicationPageProps): Promise<Metadata> {
  const { slug } = await params;
  const app = getApplicationBySlug(slug);
  if (!app) return {};
  return buildPageMetadata({
    title: app.metaTitle,
    description: app.description,
    path: app.href,
  });
}

export default async function ApplicationPage({ params }: ApplicationPageProps) {
  const { slug } = await params;
  const app = getApplicationBySlug(slug);
  if (!app) notFound();

  const pageSlug = `applications-${slug}`;
  const page = await getPage(pageSlug);
  const products = await getProducts({ category: app.categorySlug, page_size: 4 });

  return (
    <div className="section-py">
      <div className="container-page">
        <Breadcrumbs
          items={[
            { label: "Главная", href: "/" },
            { label: "Применение", href: "/applications/crane" },
            { label: app.title },
          ]}
          className="mb-6"
        />
        <h1 className="font-display text-3xl font-bold md:text-4xl">{app.title}</h1>
        <p className="mt-4 max-w-3xl text-muted-foreground">{app.description}</p>
        {page && (
          <div
            className="prose prose-slate mt-6 max-w-none"
            dangerouslySetInnerHTML={{ __html: page.body }}
          />
        )}
        <section className="mt-12">
          <h2 className="font-display text-xl font-semibold">Рекомендуемые позиции</h2>
          <ul className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {products.results.map((product) => (
              <li key={product.id}>
                <ProductCard product={product} categoryPath={[product.category_slug]} />
              </li>
            ))}
          </ul>
          <Link href={`/catalog/${app.categorySlug}`} className="mt-6 inline-block text-primary hover:underline">
            Смотреть весь каталог →
          </Link>
        </section>
      </div>
    </div>
  );
}
