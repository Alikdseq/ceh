import { describe, expect, it } from "vitest";

import { isProductImagePlaceholder, productImageSrc } from "@/lib/utils";

describe("productImageSrc", () => {
  it("prefers CMS media URL over static /tovar fallback", () => {
    const cmsUrl = "https://www.ekontaktor.ru/media/products/kt6052-custom.jpg";
    const result = productImageSrc(cmsUrl, {
      series_code: "6052",
      product_type: "KT",
      name: "КТ6052Б",
    });
    expect(result).toContain("/media/products/kt6052-custom.jpg");
    expect(result).not.toContain("/tovar/");
  });

  it("uses static fallback only for placeholder API image", () => {
    const result = productImageSrc("/placeholder-product.svg", {
      series_code: "6052",
      product_type: "KT",
      name: "КТ6052Б",
    }, true);
    expect(result).toContain("/tovar/");
    expect(decodeURIComponent(result)).toMatch(/6052/i);
  });

  it("detects placeholder images", () => {
    expect(isProductImagePlaceholder("/placeholder-product.svg", true)).toBe(true);
    expect(isProductImagePlaceholder("/media/products/x.jpg", false)).toBe(false);
  });
});
