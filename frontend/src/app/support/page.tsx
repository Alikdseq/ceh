import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { ContentPageLayout } from "@/components/content/ContentPageLayout";
import { FAQList } from "@/components/content/FAQList";
import { SupportContactSection } from "@/components/content/SupportContactSection";
import { JsonLd } from "@/components/seo/JsonLd";
import { getFAQ, getPage } from "@/lib/api/content";
import { buildFAQPageSchema } from "@/lib/schema";
import { buildCmsPageMetadata } from "@/lib/seo";

export async function generateMetadata(): Promise<Metadata> {
  const page = await getPage("support");
  if (!page) {
    return buildCmsPageMetadata(
      { title: "Поддержка", meta_title: "Поддержка", meta_description: "FAQ и контакты отдела сбыта." },
      "/support/",
    );
  }
  return buildCmsPageMetadata(page, "/support/");
}

export default async function SupportPage() {
  const [page, faq] = await Promise.all([getPage("support"), getFAQ()]);
  if (!page) notFound();

  const faqSchema = buildFAQPageSchema(faq);

  return (
    <>
      {faqSchema ? <JsonLd data={faqSchema} /> : null}
      <ContentPageLayout
      page={page}
      breadcrumbs={[
        { label: "Главная", href: "/" },
        { label: "Поддержка" },
      ]}
    >
      <section className="mt-10">
        <h2 className="font-display text-xl font-semibold">Частые вопросы</h2>
        <div className="mt-4">
          <FAQList items={faq} />
        </div>
      </section>
      <SupportContactSection />
    </ContentPageLayout>
    </>
  );
}
