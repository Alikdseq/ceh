import { describe, expect, it } from "vitest";

import {
  buildFAQPageSchema,
  buildNewsArticleSchema,
  buildProductSchema,
  buildWebSiteSchema,
} from "@/lib/schema";

describe("schema builders", () => {
  it("builds product schema with nested category path", () => {
    const schemas = buildProductSchema(
      {
        name: "Контактор КТ 6043",
        slug: "kontaktor-kt-6043",
        short_description: "400А",
        category_slug: "kt-6000",
        category_path: ["kontaktory-kt", "kt-6000"],
        price_from: "100000",
        series_code: "6043",
        primary_image: { url: "https://example.com/img.webp" },
      },
      { sku_code: "KT6043B", price: "100000" },
      [
        { name: "Главная", url: "https://ekontaktor.ru" },
        { name: "Каталог", url: "https://ekontaktor.ru/catalog" },
      ],
      "https://ekontaktor.ru",
    );
    const product = schemas[0] as { offers?: { url?: string }; manufacturer?: { name?: string } };
    expect(product.offers?.url).toBe(
      "https://ekontaktor.ru/catalog/kontaktory-kt/kt-6000/kontaktor-kt-6043",
    );
    expect(product.manufacturer?.name).toContain("Электроконтактор");
  });

  it("builds FAQPage schema", () => {
    const schema = buildFAQPageSchema([
      { question: "Как заказать?", answer: "Через корзину-заявку." },
    ]);
    expect(schema?.["@type"]).toBe("FAQPage");
    expect(schema?.mainEntity).toHaveLength(1);
  });

  it("builds WebSite schema with search action", () => {
    const schema = buildWebSiteSchema();
    expect(schema["@type"]).toBe("WebSite");
    expect(schema.potentialAction?.["@type"]).toBe("SearchAction");
  });

  it("builds NewsArticle schema", () => {
    const schema = buildNewsArticleSchema({
      title: "Новость",
      excerpt: "Кратко",
      published_at: "2026-01-01T00:00:00Z",
      slug: "news-1",
    });
    expect(schema["@type"]).toBe("NewsArticle");
    expect(schema.url).toContain("/news/news-1/");
  });
});
