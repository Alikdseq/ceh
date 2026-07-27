import { describe, expect, it } from "vitest";

import { buildRobotsTxt } from "@/lib/robots-txt";

describe("buildRobotsTxt", () => {
  it("blocks service and duplicate URLs", () => {
    const text = buildRobotsTxt("https://www.ekontaktor.ru");
    expect(text).toContain("Disallow: /search");
    expect(text).toContain("Disallow: /cart/");
    expect(text).toContain("Disallow: /manage/");
    expect(text).toContain("Disallow: /*?variant=");
    expect(text).toContain("Sitemap: https://www.ekontaktor.ru/sitemap.xml");
  });

  it("includes Yandex Host and Clean-param", () => {
    const text = buildRobotsTxt("https://www.ekontaktor.ru");
    expect(text).toContain("User-agent: Yandex");
    expect(text).toContain("Host: www.ekontaktor.ru");
    expect(text).toContain("Clean-param: utm_source");
    expect(text).toContain("Clean-param: page&page_size");
    expect(text).toContain("Clean-param: variant /catalog/");
  });
});
