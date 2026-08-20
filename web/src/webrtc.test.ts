import { describe, expect, it, vi } from "vitest";
import { TeamPeer } from "./webrtc";

describe("TeamPeer", () => {
  it("queues ICE candidates until a remote description exists", async () => {
    const signals: unknown[] = [];
    const peer = new TeamPeer({ onSignal: (message) => signals.push(message) });

    await peer.handleSignal({
      type: "ice",
      candidate: { candidate: "candidate:test", sdpMid: "0", sdpMLineIndex: 0 },
    });

    expect(signals).toHaveLength(0);
    peer.close();
  });

  it("reports a closed state when explicitly closed", () => {
    const states: string[] = [];
    const peer = new TeamPeer({ onSignal: vi.fn(), onState: (state) => states.push(state) });
    peer.close();
    expect(states.at(-1)).toBe("closed");
  });
});
