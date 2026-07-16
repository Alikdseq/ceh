import { describe, expect, it } from "vitest";

import { normalizeMediaUrl } from "@/lib/utils";

describe("normalizeMediaUrl", () => {
  it("rewrites internal backend media URL to same-origin path", () => {
    expect(normalizeMediaUrl("http://backend:8000/media/products/x.jpg")).toBe("/media/products/x.jpg");
  });

  it("keeps public https URLs", () => {
    const url = "https://www.ekontaktor.ru/media/products/x.jpg";
    expect(normalizeMediaUrl(url)).toBe(url);
  });
});
