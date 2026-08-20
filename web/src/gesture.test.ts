import { describe, expect, it } from "vitest";
import { GestureEngine } from "./gesture";

describe("GestureEngine", () => {
  it("requires consecutive frames", () => {
    const engine = new GestureEngine({ confirmationFrames: 3, cooldownMs: 0 });
    expect(engine.update("pinch", 0)).toBeNull();
    expect(engine.update("pinch", 10)).toBeNull();
    expect(engine.update("pinch", 20)).toBe("pinch");
  });

  it("rearms only after none", () => {
    const engine = new GestureEngine({ confirmationFrames: 2, cooldownMs: 0 });
    expect(engine.update("pinch", 0)).toBeNull();
    expect(engine.update("pinch", 10)).toBe("pinch");
    expect(engine.update("pinch", 20)).toBeNull();
    expect(engine.update("none", 30)).toBeNull();
    expect(engine.update("pinch", 40)).toBeNull();
    expect(engine.update("pinch", 50)).toBe("pinch");
  });

  it("rejects invalid configuration", () => {
    expect(() => new GestureEngine({ confirmationFrames: 0, cooldownMs: 0 })).toThrow();
    expect(() => new GestureEngine({ confirmationFrames: 1, cooldownMs: -1 })).toThrow();
  });
});
