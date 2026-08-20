import { describe, expect, it } from "vitest";
import { canUsePermission, createTeamCode, normalizeTeamCode, validTeamCode } from "./team";

describe("Team View", () => {
  it("creates a correctly shaped deterministic code", () => {
    expect(createTeamCode(() => 0)).toBe("HM-AAAA-AAAA");
  });

  it("normalizes and validates team codes", () => {
    expect(normalizeTeamCode(" hm-abcd-2345 ")).toBe("HM-ABCD-2345");
    expect(validTeamCode("hm-abcd-2345")).toBe(true);
    expect(validTeamCode("HM-ABCD-123")).toBe(false);
    expect(validTeamCode("HM-ABCD-12345")).toBe(false);
  });

  it("requires explicit permissions", () => {
    expect(canUsePermission(["screen"], "screen")).toBe(true);
    expect(canUsePermission(["screen"], "control")).toBe(false);
  });
});
