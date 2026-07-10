import type { Metadata } from "next";

import { ContentPageLayout } from "@/components/content/ContentPageLayout";
import { getCookiesPage } from "@/lib/legal-content";

export async function generateMetadata(): Promise<Metadata> {
  const page = getCookiesPage();
  return { title: page.meta_title, description: page.meta_description };
}

export default function CookiesPage() {
  const page = getCookiesPage();
  return (
    <ContentPageLayout
      page={page}
      breadcrumbs={[{ label: "Главная", href: "/" }, { label: page.title }]}
    />
  );
}

