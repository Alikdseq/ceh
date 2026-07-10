import { describe, expect, it } from "vitest";

import { buildBackendApiUrl } from "@/lib/api/proxy";

describe("buildBackendApiUrl", () => {
  it("adds trailing slash before query string for Django", () => {
    expect(buildBackendApiUrl("/api/v1/compare", "?ids=103,115")).toBe(
      "http://127.0.0.1:8000/api/v1/compare/?ids=103,115",
    );
  });

  it("keeps existing trailing slash", () => {
    expect(buildBackendApiUrl("/api/v1/compare/", "?ids=1")).toBe(
      "http://127.0.0.1:8000/api/v1/compare/?ids=1",
    );
  });
});
