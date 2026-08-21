import { test, expect } from "@playwright/test";

async function waitForIceGathering(page: import("@playwright/test").Page): Promise<void> {
  await page.evaluate(async () => {
    const pc = (window as Window & { __handMousePc?: RTCPeerConnection }).__handMousePc;
    if (!pc) throw new Error("Peer connection was not initialized");
    if (pc.iceGatheringState === "complete") return;
    await new Promise<void>((resolve, reject) => {
      const timeout = window.setTimeout(() => reject(new Error("ICE gathering timeout")), 10_000);
      pc.addEventListener("icegatheringstatechange", () => {
        if (pc.iceGatheringState === "complete") {
          window.clearTimeout(timeout);
          resolve();
        }
      });
    });
  });
}

test("two independent Chromium pages establish a real WebRTC data channel", async ({ browser }) => {
  const a = await browser.newPage();
  const b = await browser.newPage();

  await Promise.all([a.goto("about:blank"), b.goto("about:blank")]);

  await a.evaluate(() => {
    const pc = new RTCPeerConnection({ iceServers: [] });
    const channel = pc.createDataChannel("hand-mouse-test", { ordered: true });
    (window as Window & { __handMousePc?: RTCPeerConnection; __handMouseChannel?: RTCDataChannel }).__handMousePc = pc;
    (window as Window & { __handMousePc?: RTCPeerConnection; __handMouseChannel?: RTCDataChannel }).__handMouseChannel = channel;
  });

  await b.evaluate(() => {
    const pc = new RTCPeerConnection({ iceServers: [] });
    (window as Window & { __handMousePc?: RTCPeerConnection; __handMouseReceived?: Promise<string> }).__handMousePc = pc;
    (window as Window & { __handMousePc?: RTCPeerConnection; __handMouseReceived?: Promise<string> }).__handMouseReceived = new Promise<string>((resolve, reject) => {
      const timer = window.setTimeout(() => reject(new Error("DataChannel message timeout")), 10_000);
      pc.ondatachannel = (event) => {
        event.channel.onmessage = (message) => {
          window.clearTimeout(timer);
          resolve(String(message.data));
        };
      };
    });
  });

  const offer = await a.evaluate(async () => {
    const pc = (window as Window & { __handMousePc?: RTCPeerConnection }).__handMousePc!;
    await pc.setLocalDescription(await pc.createOffer());
    return new Promise<RTCSessionDescriptionInit>((resolve, reject) => {
      const timeout = window.setTimeout(() => reject(new Error("Offer ICE gathering timeout")), 10_000);
      const finish = () => {
        if (!pc.localDescription) return;
        window.clearTimeout(timeout);
        resolve({ type: pc.localDescription.type, sdp: pc.localDescription.sdp });
      };
      if (pc.iceGatheringState === "complete") finish();
      else pc.addEventListener("icegatheringstatechange", () => {
        if (pc.iceGatheringState === "complete") finish();
      });
    });
  });

  const answer = await b.evaluate(async (remoteOffer) => {
    const pc = (window as Window & { __handMousePc?: RTCPeerConnection }).__handMousePc!;
    await pc.setRemoteDescription(remoteOffer);
    await pc.setLocalDescription(await pc.createAnswer());
    return new Promise<RTCSessionDescriptionInit>((resolve, reject) => {
      const timeout = window.setTimeout(() => reject(new Error("Answer ICE gathering timeout")), 10_000);
      const finish = () => {
        if (!pc.localDescription) return;
        window.clearTimeout(timeout);
        resolve({ type: pc.localDescription.type, sdp: pc.localDescription.sdp });
      };
      if (pc.iceGatheringState === "complete") finish();
      else pc.addEventListener("icegatheringstatechange", () => {
        if (pc.iceGatheringState === "complete") finish();
      });
    });
  }, offer);

  await a.evaluate(async (remoteAnswer) => {
    const pc = (window as Window & { __handMousePc?: RTCPeerConnection }).__handMousePc!;
    await pc.setRemoteDescription(remoteAnswer);
  }, answer);

  await a.evaluate(async () => {
    const channel = (window as Window & { __handMouseChannel?: RTCDataChannel }).__handMouseChannel!;
    if (channel.readyState !== "open") {
      await new Promise<void>((resolve, reject) => {
        const timeout = window.setTimeout(() => reject(new Error("DataChannel open timeout")), 10_000);
        channel.addEventListener("open", () => {
          window.clearTimeout(timeout);
          resolve();
        }, { once: true });
      });
    }
    channel.send("HAND-MOUSE-WEBRTC-OK");
  });

  const received = await b.evaluate(async () => {
    const state = window as Window & { __handMouseReceived?: Promise<string> };
    return state.__handMouseReceived;
  });

  expect(received).toBe("HAND-MOUSE-WEBRTC-OK");

  await Promise.all([
    a.evaluate(() => (window as Window & { __handMousePc?: RTCPeerConnection }).__handMousePc?.close()),
    b.evaluate(() => (window as Window & { __handMousePc?: RTCPeerConnection }).__handMousePc?.close()),
    a.close(),
    b.close(),
  ]);
});
