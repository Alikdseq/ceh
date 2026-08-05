import type { Metadata } from "next";
import Link from "next/link";

import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { SubscribeForm } from "@/components/home/SubscribeForm";
import { NewsPostThumbnail } from "@/components/news/NewsPostThumbnail";
import { getNewsList } from "@/lib/api/content";

export const metadata: Metadata = {
  title: "Новости",
  description: "Новости и анонсы АО «Электроконтактор»",
};

interface NewsPageProps {
  searchParams: Promise<{ page?: string }>;
}

export default async function NewsPage({ searchParams }: NewsPageProps) {
  const { page: pageParam } = await searchParams;
  const page = Number(pageParam ?? 1);
  const data = await getNewsList(page);
  const totalPages = Math.max(1, Math.ceil(data.count / 24));

  return (
    <div className="section-py">
      <div className="container-page">
        <Breadcrumbs
          items={[{ label: "Главная", href: "/" }, { label: "Новости" }]}
          className="mb-6"
        />
        <div className="grid gap-10 lg:grid-cols-[1fr_280px]">
          <div>
            <h1 className="font-display text-3xl font-bold">Новости</h1>
            <ul className="mt-8 divide-y">
              {data.results.map((post) => (
                <li key={post.id} className="py-6">
                  <Link href={`/news/${post.slug}`} className="group flex gap-4 sm:gap-5">
                    {post.image_url && (
                      <NewsPostThumbnail
                        src={post.image_url}
                        alt={post.title}
                        className="aspect-[4/3] h-24 w-32 shrink-0 sm:h-28 sm:w-40"
                        sizes="160px"
                      />
                    )}
                    <div className="min-w-0 flex-1">
                    <time className="text-sm text-muted-foreground">
                      {new Date(post.published_at).toLocaleDateString("ru-RU")}
                    </time>
                    <h2 className="mt-1 font-display text-xl font-semibold group-hover:text-primary">
                      {post.title}
                    </h2>
                    <p className="mt-2 text-muted-foreground">{post.excerpt}</p>
                    </div>
                  </Link>
                </li>
              ))}
            </ul>
            {totalPages > 1 && (
              <nav className="mt-8 flex gap-2" aria-label="Пагинация">
                {page > 1 && (
                  <Link href={`/news?page=${page - 1}`} className="text-primary hover:underline">
                    ← Назад
                  </Link>
                )}
                <span className="text-muted-foreground">
                  {page} / {totalPages}
                </span>
                {page < totalPages && (
                  <Link href={`/news?page=${page + 1}`} className="text-primary hover:underline">
                    Вперёд →
                  </Link>
                )}
              </nav>
            )}
          </div>
          <aside className="rounded-lg border p-5 h-fit">
            <p className="font-semibold">Подписка</p>
            <p className="mt-1 text-sm text-muted-foreground">Анонсы и обновления прайса</p>
            <SubscribeForm variant="sidebar" />
            <Link href="/news/rss.xml" className="mt-4 block text-sm text-primary hover:underline">
              RSS-лента
            </Link>
          </aside>
        </div>
      </div>
    </div>
  );
}
