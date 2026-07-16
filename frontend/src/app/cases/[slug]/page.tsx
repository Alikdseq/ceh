import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { ProductCard } from "@/components/catalog/ProductCard";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { JsonLd } from "@/components/seo/JsonLd";
import { getCaseStudy } from "@/lib/api";
import { buildCaseStudySchema } from "@/lib/schema";
import { buildPageMetadata } from "@/lib/seo";

interface CasePageProps {
  params: Promise<{ slug: string }>;
}

export async function generateMetadata({ params }: CasePageProps): Promise<Metadata> {
  const { slug } = await params;
  const study = await getCaseStudy(slug);
  if (!study) return {};
  return buildPageMetadata({
    title: study.meta_title || study.title,
    description: study.meta_description || study.excerpt,
    path: `/cases/${slug}/`,
  });
}

export default async function CaseDetailPage({ params }: CasePageProps) {
  const { slug } = await params;
  const study = await getCaseStudy(slug);
  if (!study) notFound();

  return (
    <>
      <JsonLd data={buildCaseStudySchema(study)} />
      <div className="section-py">
        <div className="container-page">
          <Breadcrumbs
            items={[
              { label: "Главная", href: "/" },
              { label: "Кейсы", href: "/cases/" },
              { label: study.title },
            ]}
            className="mb-6"
          />
          {study.industry && (
            <p className="text-sm font-medium text-primary">{study.industry}</p>
          )}
          <h1 className="font-display text-3xl font-bold md:text-4xl">{study.title}</h1>
          {study.excerpt && <p className="mt-4 max-w-3xl text-lg text-muted-foreground">{study.excerpt}</p>}
          <div
            className="prose prose-slate mt-8 max-w-none"
            dangerouslySetInnerHTML={{ __html: study.body }}
          />
          {study.products.length > 0 && (
            <section className="mt-12">
              <h2 className="font-display text-xl font-semibold">Использованная продукция</h2>
              <ul className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                {study.products.map((product) => (
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
          <Link href="/cases/" className="mt-10 inline-block text-primary hover:underline">
            ← Все кейсы
          </Link>
        </div>
      </div>
    </>
  );
}
