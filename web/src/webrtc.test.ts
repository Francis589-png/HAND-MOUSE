import { describe, expect, it } from "vitest";

describe("WebRTC runtime", () => {
  it("does not pretend WebRTC exists in a non-browser runtime", () => {
    expect(typeof globalThis.RTCPeerConnection).toBe("undefined");
  });

  it("exposes the browser WebRTC API when available", () => {
    if (typeof globalThis.RTCPeerConnection === "undefined") return;
    expect(typeof globalThis.RTCPeerConnection).toBe("function");
  });
});
