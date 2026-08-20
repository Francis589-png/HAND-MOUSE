import { test, expect } from "@playwright/test";

test("two real Chromium peers establish a WebRTC data channel", async ({ browser }) => {
  const a = await browser.newPage();
  const b = await browser.newPage();

  await Promise.all([a.goto("about:blank"), b.goto("about:blank")]);

  const result = await a.evaluate(async () => {
    const pcA = new RTCPeerConnection({ iceServers: [] });
    const pcB = new RTCPeerConnection({ iceServers: [] });
    const channel = pcA.createDataChannel("hand-mouse-test");
    const received = new Promise<string>((resolve, reject) => {
      const timer = window.setTimeout(() => reject(new Error("DataChannel message timeout")), 10_000);
      pcB.ondatachannel = (event) => {
        event.channel.onmessage = (message) => {
          window.clearTimeout(timer);
          resolve(String(message.data));
        };
      };
    });

    const candidatesA: RTCIceCandidateInit[] = [];
    const candidatesB: RTCIceCandidateInit[] = [];
    pcA.onicecandidate = (event) => { if (event.candidate) candidatesA.push(event.candidate.toJSON()); };
    pcB.onicecandidate = (event) => { if (event.candidate) candidatesB.push(event.candidate.toJSON()); };

    await pcA.setLocalDescription(await pcA.createOffer());
    await pcB.setRemoteDescription(pcA.localDescription!);
    await pcB.setLocalDescription(await pcB.createAnswer());
    await pcA.setRemoteDescription(pcB.localDescription!);

    await new Promise<void>((resolve, reject) => {
      const deadline = Date.now() + 10_000;
      const timer = window.setInterval(async () => {
        try {
          for (const candidate of candidatesA) await pcB.addIceCandidate(candidate);
          candidatesA.length = 0;
          for (const candidate of candidatesB) await pcA.addIceCandidate(candidate);
          candidatesB.length = 0;
          if (pcA.iceConnectionState === "connected" || pcA.iceConnectionState === "completed") {
            window.clearInterval(timer);
            resolve();
          } else if (Date.now() > deadline) {
            window.clearInterval(timer);
            reject(new Error(`ICE failed: ${pcA.iceConnectionState}/${pcB.iceConnectionState}`));
          }
        } catch (error) {
          window.clearInterval(timer);
          reject(error);
        }
      }, 50);
    });

    await new Promise<void>((resolve, reject) => {
      const timer = window.setTimeout(() => reject(new Error("DataChannel open timeout")), 10_000);
      if (channel.readyState === "open") {
        window.clearTimeout(timer);
        resolve();
      } else channel.onopen = () => { window.clearTimeout(timer); resolve(); };
    });

    channel.send("HAND-MOUSE-WEBRTC-OK");
    const message = await received;
    pcA.close();
    pcB.close();
    return message;
  });

  expect(result).toBe("HAND-MOUSE-WEBRTC-OK");
  await a.close();
  await b.close();
});
