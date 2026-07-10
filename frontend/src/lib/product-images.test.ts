import { describe, expect, it } from "vitest";

import { resolveStaticProductGallery, resolveStaticProductImage } from "@/lib/product-images";

describe("product-images", () => {
  it("maps KT series to static photo", () => {
    const url = resolveStaticProductImage({
      series_code: "6043",
      product_type: "KT",
      name: "Контактор КТ 6043Б (400А)",
      slug: "kontaktor-kt-6043",
    });
    expect(url).toContain("/tovar/");
    expect(decodeURIComponent(url ?? "")).toMatch(/6043/i);
  });

  it("maps KTP series to static photo", () => {
    const url = resolveStaticProductImage({
      series_code: "6012",
      product_type: "KTP",
      name: "Контактор КТП 6012Б",
      slug: "kontaktor-ktp-6012",
    });
    expect(url).toContain("/tovar/");
    expect(decodeURIComponent(url ?? "")).toMatch(/6012/i);
  });

  it("resolves from SKU in cart context", () => {
    const url = resolveStaticProductImage({
      sku_code: "КТ6043Б-У3",
      name: "Контактор КТ 6043Б",
    });
    expect(url).toBeTruthy();
  });

  it("returns gallery with alternate angles", () => {
    const gallery = resolveStaticProductGallery({
      series_code: "6043",
      product_type: "KTP",
      name: "Контактор КТП 6043Б",
    });
    expect(gallery.length).toBeGreaterThanOrEqual(1);
  });

  it("returns null for unknown series", () => {
    const url = resolveStaticProductImage({
      series_code: "9999",
      product_type: "KT",
      name: "Контактор КТ 9999",
    });
    expect(url).toBeNull();
  });
});
