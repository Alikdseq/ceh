import type { Metadata } from "next";
import Link from "next/link";

import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { getCaseStudies } from "@/lib/api";
import { buildPageMetadata } from "@/lib/seo";

export const metadata: Metadata = buildPageMetadata({
  title: "Реализованные объекты и кейсы",
  description:
    "Примеры поставок контакторов КТ, КТП и КТЭ АО «Электроконтактор» на промышленные объекты по России.",
  path: "/cases/",
});

export default async function CasesIndexPage() {
  const cases = await getCaseStudies();

  return (
    <div className="section-py">
      <div className="container-page">
        <Breadcrumbs
          items={[
            { label: "Главная", href: "/" },
            { label: "Кейсы и объекты" },
          ]}
          className="mb-6"
        />
        <h1 className="font-display text-3xl font-bold md:text-4xl">Реализованные объекты</h1>
        <p className="mt-3 max-w-2xl text-muted-foreground">
          Опыт внедрения продукции завода в крановое, энергетическое и транспортное оборудование.
        </p>
        <ul className="mt-10 grid gap-6 md:grid-cols-2">
          {cases.map((item) => (
            <li key={item.slug}>
              <Link
                href={`/cases/${item.slug}/`}
                className="block rounded-xl border bg-card p-6 shadow-sm transition-shadow hover:shadow-md"
              >
                {item.industry && (
                  <p className="text-xs font-medium uppercase tracking-wide text-primary">{item.industry}</p>
                )}
                <h2 className="mt-2 font-display text-lg font-semibold">{item.title}</h2>
                <p className="mt-2 text-sm text-muted-foreground">{item.excerpt}</p>
              </Link>
            </li>
          ))}
        </ul>
        {cases.length === 0 && (
          <p className="mt-8 text-muted-foreground">Кейсы скоро появятся в этом разделе.</p>
        )}
      </div>
    </div>
  );
}
