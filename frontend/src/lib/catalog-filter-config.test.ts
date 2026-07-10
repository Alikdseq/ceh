import { describe, expect, it } from "vitest";

import { getAvailableFilters, hasCatalogFilters } from "@/lib/catalog-filter-config";
import { phoneToTelHref } from "@/lib/site-links";

describe("catalog-filter-config", () => {
  it("shows full KT filters for kontaktory-kt subtree", () => {
    const filters = getAvailableFilters(["kontaktory-kt", "kt-6000b"]);
    expect(filters).toContain("current");
    expect(filters).toContain("coil");
    expect(filters).not.toContain("product_type");
  });

  it("hides filters for accessories and switches", () => {
    expect(hasCatalogFilters(["aksessuary-kontaktorov", "meh-blokirovki"])).toBe(false);
    expect(hasCatalogFilters(["paketnye-pereklyuchateli", "pvp-17-29"])).toBe(false);
  });
});

describe("phoneToTelHref", () => {
  it("formats factory phone", () => {
    expect(phoneToTelHref("(8672) 53-33-44")).toBe("tel:+78672533344");
  });
});
