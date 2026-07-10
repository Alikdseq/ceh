import type { Metadata } from "next";
import Link from "next/link";

import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { APPLICATION_PAGES } from "@/lib/applications";
import { buildPageMetadata } from "@/lib/seo";

export const metadata: Metadata = buildPageMetadata({
  title: "Применение контакторов — отраслевые решения",
  description:
    "Контакторы АО «Электроконтактор» для кранового оборудования, НКУ и электротранспорта. Прямые поставки от производителя.",
  path: "/applications/",
});

export default function ApplicationsIndexPage() {
  return (
    <div className="section-py">
      <div className="container-page">
        <Breadcrumbs
          items={[
            { label: "Главная", href: "/" },
            { label: "Применение" },
          ]}
          className="mb-6"
        />
        <h1 className="font-display text-3xl font-bold md:text-4xl">Применение продукции</h1>
        <p className="mt-3 max-w-2xl text-muted-foreground">
          Отраслевые решения на базе контакторов КТ, КТП и КТЭ для промышленности и транспорта.
        </p>
        <ul className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {APPLICATION_PAGES.map((app) => (
            <li key={app.slug}>
              <Link
                href={app.href}
                className="block rounded-xl border bg-card p-6 shadow-sm transition-shadow hover:shadow-md"
              >
                <h2 className="font-display text-lg font-semibold">{app.title}</h2>
                <p className="mt-2 text-sm text-muted-foreground">{app.description}</p>
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
