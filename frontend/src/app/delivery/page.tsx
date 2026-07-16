import type { Metadata } from "next";
import Link from "next/link";

import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { getDeliveryCities } from "@/lib/api";
import { buildPageMetadata } from "@/lib/seo";

export const metadata: Metadata = buildPageMetadata({
  title: "Доставка контакторов по России",
  description:
    "Прямые поставки контакторов КТ, КТП, КТЭ с завода Электроконтактор в регионы РФ. Документация и заявка онлайн.",
  path: "/delivery/",
});

export default async function DeliveryIndexPage() {
  const cities = await getDeliveryCities();

  return (
    <div className="section-py">
      <div className="container-page">
        <Breadcrumbs
          items={[
            { label: "Главная", href: "/" },
            { label: "Доставка по России" },
          ]}
          className="mb-6"
        />
        <h1 className="font-display text-3xl font-bold md:text-4xl">Поставки по регионам России</h1>
        <p className="mt-3 max-w-2xl text-muted-foreground">
          Отгрузка с завода во Владикавказе транспортными компаниями. Публичные цены производителя с НДС.
        </p>
        <ul className="mt-10 columns-1 gap-x-8 sm:columns-2 lg:columns-3">
          {cities.map((city) => (
            <li key={city.slug} className="mb-3 break-inside-avoid">
              <Link href={`/delivery/${city.slug}/`} className="text-primary hover:underline">
                Контакторы — {city.name}
                {city.region_name ? ` (${city.region_name})` : ""}
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
