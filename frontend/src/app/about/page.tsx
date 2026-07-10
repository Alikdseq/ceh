import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";

import { ContentPageLayout } from "@/components/content/ContentPageLayout";
import { getPage } from "@/lib/api/content";
import { buildCmsPageMetadata } from "@/lib/seo";

export async function generateMetadata(): Promise<Metadata> {
  const page = await getPage("about");
  if (!page) return {};
  return buildCmsPageMetadata(page, "/about/");
}

export default async function AboutPage() {
  const page = await getPage("about");
  if (!page) notFound();

  return (
    <ContentPageLayout
      page={page}
      breadcrumbs={[
        { label: "Главная", href: "/" },
        { label: "О заводе", href: "/about" },
      ]}
    >
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

      <nav className="mt-6 flex flex-wrap gap-3 text-sm">
        <Link href="/about/production" className="text-primary hover:underline">
          Производство
        </Link>
        <Link href="/about/certificates" className="text-primary hover:underline">
          Сертификаты
        </Link>
      </nav>
    </ContentPageLayout>
  );
}
