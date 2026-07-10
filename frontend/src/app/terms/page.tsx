import type { Metadata } from "next";

import { ContentPageLayout } from "@/components/content/ContentPageLayout";
import { getTermsPage } from "@/lib/legal-content";

export async function generateMetadata(): Promise<Metadata> {
  const page = getTermsPage();
  return { title: page.meta_title, description: page.meta_description };
}

export default function TermsPage() {
  const page = getTermsPage();
  return (
    <ContentPageLayout
      page={page}
      breadcrumbs={[{ label: "Главная", href: "/" }, { label: page.title }]}
    />
  );
}
