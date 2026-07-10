import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { ContactsInfoBlock } from "@/components/content/ContactsInfoBlock";
import { YandexMap } from "@/components/content/YandexMap";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { ContactsActions } from "@/components/leads/ContactsActions";
import { getPage, getSiteSettings } from "@/lib/api/content";
import { buildCmsPageMetadata } from "@/lib/seo";

export async function generateMetadata(): Promise<Metadata> {
  const page = await getPage("contacts");
  if (!page) return {};
  return buildCmsPageMetadata(page, "/contacts/");
}

export default async function ContactsPage() {
  const [page, settings] = await Promise.all([getPage("contacts"), getSiteSettings()]);
  if (!page) notFound();
  const address = settings?.address ?? "362003, г. Владикавказ, ул. Кабардинская, 8";

  return (
    <div className="section-py">
      <div className="container-page">
        <Breadcrumbs
          items={[
            { label: "Главная", href: "/" },
            { label: "Контакты" },
          ]}
          className="mb-6"
        />
        <h1 className="font-display text-3xl font-bold md:text-4xl">{page.h1 || page.title}</h1>

        <div className="mt-8 grid gap-6 lg:grid-cols-[minmax(0,1fr)_260px] lg:items-start">
          <YandexMap address={address} className="min-w-0" />
          <aside className="flex flex-col gap-4 lg:w-[260px] lg:shrink-0">
            <ContactsInfoBlock settings={settings} />
            <div className="rounded-lg border p-4 lg:p-5">
              <p className="font-display font-semibold">Связаться с нами</p>
              <div className="mt-3">
                <ContactsActions />
              </div>
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
}
