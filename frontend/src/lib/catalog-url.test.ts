import { describe, expect, it } from "vitest";

import { catalogProductPath } from "./catalog-url";

describe("catalogProductPath", () => {
  it("uses full category_path when provided", () => {
    expect(
      catalogProductPath({
        slug: "kontaktor-kt-6022-160a-b",
        category_path: ["kontaktory-kt", "kt-6000b"],
      }),
    ).toBe("/catalog/kontaktory-kt/kt-6000b/kontaktor-kt-6022-160a-b");
  });
});
