import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { JsonLd } from "@/components/seo/JsonLd";
import { getNewsDetail } from "@/lib/api/content";
import { buildNewsArticleSchema } from "@/lib/schema";
import { buildNewsMetadata } from "@/lib/seo";

interface NewsArticleProps {
  params: Promise<{ slug: string }>;
}

export async function generateMetadata({ params }: NewsArticleProps): Promise<Metadata> {
  const { slug } = await params;
  const post = await getNewsDetail(slug);
  if (!post) return {};
  return buildNewsMetadata(post, slug);
}

export default async function NewsArticlePage({ params }: NewsArticleProps) {
  const { slug } = await params;
  const post = await getNewsDetail(slug);
  if (!post) notFound();

  return (
    <>
      <JsonLd data={buildNewsArticleSchema(post)} />
      <article className="section-py">
      <div className="container-page max-w-3xl">
        <Breadcrumbs
          items={[
            { label: "Главная", href: "/" },
            { label: "Новости", href: "/news" },
            { label: post.title },
          ]}
          className="mb-6"
        />
        <time className="text-sm text-muted-foreground">
          {new Date(post.published_at).toLocaleDateString("ru-RU", {
            day: "numeric",
            month: "long",
            year: "numeric",
          })}
        </time>
        <h1 className="mt-2 font-display text-3xl font-bold md:text-4xl">{post.title}</h1>
        <div
          className="prose prose-slate mt-8 max-w-none"
          dangerouslySetInnerHTML={{ __html: post.body }}
        />
        <Link href="/news/" className="mt-10 inline-block text-primary hover:underline">
          ← Все новости
        </Link>
      </div>
    </article>
    </>
  );
}
