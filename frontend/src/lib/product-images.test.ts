import { describe, expect, it } from "vitest";

import { resolveStaticProductGallery, resolveStaticProductImage, productImageRotateClass, shouldRotateProductImage } from "@/lib/product-images";

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

  it("rotates only listed product cards", () => {
    expect(
      shouldRotateProductImage({
        name: "КТ6043Б-У3",
        product_type: "KT",
        series_code: "6043",
        execution: "B",
      }),
    ).toBe(true);
    expect(
      shouldRotateProductImage({
        name: "КТ6043БК-У3",
        product_type: "KT",
        series_code: "6043",
        execution: "BK",
      }),
    ).toBe(false);
    expect(
      shouldRotateProductImage({
        name: "КТ6012Б-У3",
        product_type: "KT",
        series_code: "6012",
        execution: "B",
      }),
    ).toBe(false);
    expect(
      shouldRotateProductImage({
        name: "КТ7223У-36V",
        product_type: "KT",
        series_code: "7223",
        coil_voltage_v: 36,
      }),
    ).toBe(true);
    expect(
      shouldRotateProductImage({
        name: "Контактор КТ 6633 (250А)",
        product_type: "KT",
        series_code: "6633",
        execution: "S",
      }),
    ).toBe(true);
    expect(
      shouldRotateProductImage({
        name: "Контактор КТ 7223 (125А)",
        product_type: "KT",
        series_code: "7223",
        coil_voltage_v: 36,
      }),
    ).toBe(true);
    expect(
      shouldRotateProductImage({
        name: "КТ6633С-У3",
        product_type: "KT",
        series_code: "6633",
        execution: "S",
      }),
    ).toBe(false);
    expect(
      shouldRotateProductImage({
        name: "КТ6053Б-У3",
        product_type: "KT",
        series_code: "6053",
        execution: "B",
      }),
    ).toBe(true);
    expect(
      shouldRotateProductImage({
        name: "КТП6014БС",
        product_type: "KTP",
        series_code: "6014",
        execution: "BS",
      }),
    ).toBe(true);
    expect(productImageRotateClass({ name: "КТ6043Б-У3", product_type: "KT", execution: "B" })).toBe(
      "rotate-90",
    );
    expect(
      shouldRotateProductImage({
        name: "КТП6633С",
        product_type: "KTP",
        series_code: "6633",
        execution: "S",
      }),
    ).toBe(true);
  });
});
