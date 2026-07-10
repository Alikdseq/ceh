import type { Metadata } from "next";

import { CategoryGrid } from "@/components/catalog/CategoryGrid";
import { FeaturedProducts } from "@/components/home/FeaturedProducts";
import {
  AntiCounterfeitBanner,
  HeroSection,
  PartnersSection,
  TrustBadges,
} from "@/components/home/HomeSections";
import { NewsSection } from "@/components/home/NewsSection";
import { SubscribeForm } from "@/components/home/SubscribeForm";
import { JsonLd } from "@/components/seo/JsonLd";
import { buildOrganizationSchema, buildWebSiteSchema } from "@/lib/schema";
import { getCategories, getFeaturedProducts, getLatestNews, getSiteSettings } from "@/lib/api";
import { buildHomeMetadata } from "@/lib/seo";

export const metadata: Metadata = buildHomeMetadata();

export default async function HomePage() {
  const [featured, news, settings, categories] = await Promise.all([
    getFeaturedProducts(4),
    getLatestNews(3),
    getSiteSettings(),
    getCategories(),
  ]);

  return (
    <>
      <JsonLd data={[buildOrganizationSchema(settings ?? undefined), buildWebSiteSchema(settings ?? undefined)]} />
      <HeroSection />
      <section className="section-py bg-background" aria-labelledby="home-catalog-heading">
        <div className="container-page">
          <h2 id="home-catalog-heading" className="font-display text-2xl font-bold md:text-3xl">
            Каталог продукции
          </h2>
          <p className="mt-3 max-w-2xl text-muted-foreground">
            Контакторы, выключатели, кулачковые элементы и аксессуары — прямо с завода.
          </p>
          <CategoryGrid categories={categories} className="mt-8" />
        </div>
      </section>
      <TrustBadges />
      <FeaturedProducts products={featured} />
      <PartnersSection />
      <NewsSection posts={news} />
      <section className="section-py hero-gradient text-white">
        <div className="container-page mx-auto max-w-xl text-center">
          <h2 className="font-display text-2xl font-bold">Подписка на новости</h2>
          <p className="mt-2 text-white/70">Узнавайте о новых сериях и обновлениях прайс-листа</p>
          <SubscribeForm variant="footer" className="mx-auto mt-4 max-w-md justify-center" />
        </div>
      </section>
      <AntiCounterfeitBanner />
    </>
  );
}
