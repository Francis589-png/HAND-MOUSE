import { describe, expect, it } from "vitest";
import { moveCommand } from "./protocol";

describe("companion protocol", () => {
  it("creates a normalized move command", () => {
    expect(moveCommand(0, 1)).toEqual({ command: "move", x: 0, y: 1 });
  });

  it("rejects non-finite coordinates", () => {
    expect(() => moveCommand(Number.NaN, 0.5)).toThrow();
    expect(() => moveCommand(0.5, Number.POSITIVE_INFINITY)).toThrow();
  });

  it("rejects coordinates outside the normalized range", () => {
    expect(() => moveCommand(-0.01, 0.5)).toThrow();
    expect(() => moveCommand(0.5, 1.01)).toThrow();
  });
});
