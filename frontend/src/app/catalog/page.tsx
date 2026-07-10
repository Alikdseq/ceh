import type { Metadata } from "next";

import { CategoryGrid } from "@/components/catalog/CategoryGrid";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { getCategories } from "@/lib/api";
import { buildPageMetadata } from "@/lib/seo";

export const metadata: Metadata = buildPageMetadata({
  title: "Каталог продукции — контакторы КТ, КТП, КТЭ от производителя",
  description:
    "Каталог контакторов КТ, КТП, КТЭ, выключателей и комплектующих АО «Электроконтактор». Прямые цены от производителя.",
  path: "/catalog/",
});

export default async function CatalogPage() {
  const categories = await getCategories();

  return (
    <div className="section-py">
      <div className="container-page">
        <Breadcrumbs items={[{ label: "Каталог" }]} className="mb-6" />
        <h1 className="font-display text-3xl font-bold md:text-4xl">Каталог продукции</h1>
        <p className="mt-3 max-w-2xl text-muted-foreground">
          Полный ассортимент завода: контакторы, выключатели, кулачковые элементы и аксессуары.
          Публичные цены, прямые поставки с производства.
        </p>

        <CategoryGrid categories={categories} className="mt-10" />

        {categories.length === 0 && (
          <p className="mt-12 text-center text-muted-foreground">
            Каталог временно недоступен. Проверьте подключение к API.
          </p>
        )}
      </div>
    </div>
  );
}
