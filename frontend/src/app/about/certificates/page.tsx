import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { ContentPageLayout } from "@/components/content/ContentPageLayout";
import { getPage } from "@/lib/api/content";
import { buildCmsPageMetadata } from "@/lib/seo";

const SLUG = "about-certificates";

export async function generateMetadata(): Promise<Metadata> {
  const page = await getPage(SLUG);
  if (!page) return {};
  return buildCmsPageMetadata(page, "/about/certificates/");
}

export default async function AboutCertificatesPage() {
  const page = await getPage(SLUG);
  if (!page) notFound();

  return (
    <ContentPageLayout
      page={page}
      breadcrumbs={[
        { label: "Главная", href: "/" },
        { label: "О заводе", href: "/about" },
        { label: page.title },
      ]}
    />
  );
}
