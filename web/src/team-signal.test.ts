import { describe, expect, it } from "vitest";
import { TeamSignalingClient } from "./team-signal";

describe("TeamSignalingClient", () => {
  it("rejects non-WebSocket URLs", () => {
    expect(() => new TeamSignalingClient("https://example.com")).toThrow();
  });

  it("requires a WebSocket URL", () => {
    expect(() => new TeamSignalingClient("wss://example.com/team")).not.toThrow();
  });
});
