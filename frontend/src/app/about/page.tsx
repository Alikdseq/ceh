import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";

import { AboutAwardsSection } from "@/components/content/AboutAwardsSection";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { getPage } from "@/lib/api/content";
import { buildCmsPageMetadata } from "@/lib/seo";

export async function generateMetadata(): Promise<Metadata> {
  const page = await getPage("about");
  if (!page) return {};
  return buildCmsPageMetadata(page, "/about/");
}

export default async function AboutPage() {
  const page = await getPage("about");
  const certificatesPage = await getPage("about-certificates");
  if (!page) notFound();

  return (
    <div className="section-py">
      <div className="container-page">
        <Breadcrumbs
          items={[
            { label: "Главная", href: "/" },
            { label: "О заводе", href: "/about" },
          ]}
          className="mb-6"
        />
        <h1 className="font-display text-3xl font-bold md:text-4xl">{page.h1 || page.title}</h1>

        <figure className="mt-8 overflow-hidden rounded-xl border bg-card shadow-md">
          <div className="relative aspect-[16/10] w-full bg-muted">
            <Image
              src="/photos/XXXL.webp"
              alt="Сборочное производство контакторов на заводе Электроконтактор"
              fill
              className="object-cover"
              sizes="(max-width: 1280px) 100vw, 1280px"
              priority
            />
          </div>
          <figcaption className="border-t bg-muted/50 px-4 py-3 text-sm text-muted-foreground">
            Производственная площадка АО «Электроконтактор», г. Владикавказ
          </figcaption>
        </figure>

        <div
          className="prose prose-slate mt-8 max-w-none"
          dangerouslySetInnerHTML={{ __html: page.body }}
        />

        <nav className="mt-8 flex flex-wrap gap-3 text-sm">
          <Link href="/about/production" className="text-primary hover:underline">
            Производство
          </Link>
          <a href="#certificates" className="text-primary hover:underline">
            Сертификаты
          </a>
          <a href="#awards" className="text-primary hover:underline">
            Награды
          </a>
        </nav>

        {certificatesPage && (
          <section id="certificates" className="mt-14 scroll-mt-28">
            <h2 className="font-display text-2xl font-bold md:text-3xl">
              {certificatesPage.h1 || certificatesPage.title}
            </h2>
            <div
              className="prose prose-slate mt-6 max-w-none"
              dangerouslySetInnerHTML={{ __html: certificatesPage.body }}
            />
          </section>
        )}

        <AboutAwardsSection className="mt-14" />
      </div>
    </div>
  );
}
