import { describe, expect, it } from "vitest";

import { formatCoilSpecValue, sortCoilVoltages } from "@/lib/coil-voltages";

describe("coil-voltages", () => {
  it("sorts catalog coil order", () => {
    expect(sortCoilVoltages([36, 220, 380, 127])).toEqual([220, 380, 36, 127]);
  });

  it("fixes duplicate V and sorts spec voltages ascending", () => {
    expect(formatCoilSpecValue("36 В, 220 В В, 380 В")).toBe("36 В, 220 В, 380 В");
  });
});
