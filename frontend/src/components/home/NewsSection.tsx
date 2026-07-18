import Link from "next/link";
import { ArrowRight } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import type { NewsPost } from "@/lib/types";
import { formatDate } from "@/lib/utils";

interface NewsSectionProps {
  posts: NewsPost[];
}

export function NewsSection({ posts }: NewsSectionProps) {
  if (posts.length === 0) return null;

  return (
    <section className="section-py bg-muted" aria-labelledby="news-heading">
      <div className="container-page">
        <div className="flex items-end justify-between gap-4">
          <h2 id="news-heading" className="font-display text-2xl font-bold md:text-3xl">
            Новости завода
          </h2>
          <Button asChild variant="ghost">
            <Link href="/news/">
              Все новости
              <ArrowRight className="h-4 w-4" />
            </Link>
          </Button>
        </div>
        <div className="mt-8 grid gap-4 md:grid-cols-3">
          {posts.map((post) => (
            <Link key={post.id} href={`/news/${post.slug}`}>
              <Card className="h-full transition hover:border-primary hover:shadow-sm">
                <CardContent className="p-5">
                  <time className="text-xs text-muted-foreground" dateTime={post.published_at}>
                    {formatDate(post.published_at)}
                  </time>
                  <h3 className="mt-2 font-display font-semibold leading-snug hover:text-primary">
                    {post.title}
                  </h3>
                  {post.excerpt && (
                    <p className="mt-2 line-clamp-3 text-sm text-muted-foreground">{post.excerpt}</p>
                  )}
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}
