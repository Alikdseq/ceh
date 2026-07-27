import { describe, expect, it } from "vitest";

import { isDimensionsSpecKey } from "@/lib/product-dimensions";
import { showHonestSignMarking } from "@/lib/honest-sign";

describe("isDimensionsSpecKey", () => {
  it("matches overall_dimensions", () => {
    expect(isDimensionsSpecKey("overall_dimensions")).toBe(true);
  });

  it("ignores unrelated keys", () => {
    expect(isDimensionsSpecKey("weight_net")).toBe(false);
  });
});

describe("showHonestSignMarking", () => {
  it("excludes KTE products", () => {
    expect(showHonestSignMarking({ product_type: "KTE" })).toBe(false);
  });

  it("includes KT products", () => {
    expect(showHonestSignMarking({ product_type: "KT" })).toBe(true);
  });
});
