import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { ContentPageLayout } from "@/components/content/ContentPageLayout";
import { DealerForm } from "@/components/leads/DealerForm";
import { getPage } from "@/lib/api/content";
import { buildCmsPageMetadata } from "@/lib/seo";

export async function generateMetadata(): Promise<Metadata> {
  const page = await getPage("dealers");
  if (!page) return {};
  return buildCmsPageMetadata(page, "/dealers/");
}

export default async function DealersPage() {
  const page = await getPage("dealers");
  if (!page) notFound();

  return (
    <ContentPageLayout
      page={page}
      breadcrumbs={[
        { label: "Главная", href: "/" },
        { label: "Дилерам" },
      ]}
    >
      <div className="mt-8 max-w-xl">
        <h2 className="font-display text-xl font-semibold">Заявка на партнёрство</h2>
        <DealerForm className="mt-4" />
      </div>
    </ContentPageLayout>
  );
}
