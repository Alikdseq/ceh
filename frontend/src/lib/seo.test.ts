import { describe, expect, it } from "vitest";

import { shouldNoindexCatalogParams } from "@/lib/catalog-params";
import {
  buildCategoryMetadata,
  buildPageMetadata,
  buildProductMetadata,
  fallbackProductDescription,
  getSiteUrl,
} from "@/lib/seo";

describe("seo helpers", () => {
  it("returns site url without trailing slash", () => {
    const url = getSiteUrl();
    expect(url).not.toMatch(/\/$/);
    expect(url).toMatch(/^https?:\/\//);
  });

  it("builds page metadata with canonical and twitter", () => {
    const meta = buildPageMetadata({
      title: "Каталог",
      description: "Описание",
      path: "/catalog/",
    });
    expect(meta.title).toBe("Каталог");
    expect(String(meta.alternates?.canonical)).toContain("/catalog/");
    expect(meta.twitter?.card).toBe("summary_large_image");
    expect(String(meta.openGraph?.url)).toContain("/catalog/");
  });

  it("builds product metadata with nested category path", () => {
    const meta = buildProductMetadata(
      {
        name: "Контактор КТ 6043",
        slug: "kontaktor-kt-6043",
        meta_title: "КТ 6043 — купить",
        meta_description: "400А",
        short_description: "Кратко",
        primary_image: { url: "https://cdn/img.webp" },
        category_path: ["kontaktory-kt", "kt-6000"],
      },
      ["kontaktory-kt", "kt-6000"],
    );
    expect(meta.title).toBe("КТ 6043 — купить");
    expect(String(meta.alternates?.canonical)).toContain(
      "/catalog/kontaktory-kt/kt-6000/kontaktor-kt-6043/",
    );
    expect(meta.openGraph?.images?.[0]).toMatchObject({ url: "https://cdn/img.webp" });
  });

  it("uses fallback product description from specs", () => {
    const desc = fallbackProductDescription({
      name: "Контактор КТ 6043",
      nominal_current_a: 400,
      poles: 3,
      price_from: "125000.00",
    });
    expect(desc).toContain("400А");
    expect(desc).toContain("3 полюса");
    expect(desc).toContain("125000.00");
  });

  it("builds category metadata with noindex for paginated urls", () => {
    const meta = buildCategoryMetadata(
      { name: "Контакторы КТ", meta_title: "", meta_description: "", description: "" },
      ["kontaktory-kt"],
      { noindexParams: true },
    );
    expect(meta.robots).toEqual({ index: false, follow: true });
    expect(String(meta.alternates?.canonical)).toContain("/catalog/kontaktory-kt/");
  });

  it("respects noindex flag", () => {
    const meta = buildPageMetadata({
      title: "Cart",
      description: "x",
      path: "/cart",
      noindex: true,
    });
    expect(meta.robots).toEqual({ index: false, follow: true });
  });
});

describe("catalog params noindex", () => {
  it("noindexes pagination and sort", () => {
    expect(shouldNoindexCatalogParams({ page: "2" })).toBe(true);
    expect(shouldNoindexCatalogParams({ ordering: "name" })).toBe(true);
    expect(shouldNoindexCatalogParams({ view: "list" })).toBe(true);
    expect(shouldNoindexCatalogParams({ current: "400" })).toBe(true);
    expect(shouldNoindexCatalogParams({ page: "1", view: "grid" })).toBe(false);
  });
});
