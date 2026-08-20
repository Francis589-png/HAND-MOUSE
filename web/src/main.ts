import "./style.css";
import { GestureEngine } from "./gesture";
import { moveCommand } from "./protocol";
import { HandVision, pinchDistance, pointerPosition } from "./vision";

const app = document.querySelector<HTMLDivElement>("#app");
if (!app) throw new Error("Application root not found");

app.innerHTML = `
  <section class="shell">
    <header>
      <div>
        <p class="eyebrow">JUSU • HAND-MOUSE</p>
        <h1>HAND-MOUSE Web</h1>
        <p class="muted">Control a paired desktop with your hand. Camera processing stays on this device.</p>
      </div>
      <span id="status" class="status">Disconnected</span>
    </header>

    <section class="panel controls">
      <label>Companion URL
        <input id="url" value="ws://127.0.0.1:8765" autocomplete="off" spellcheck="false" />
      </label>
      <label>Pairing token
        <input id="token" type="password" autocomplete="off" />
      </label>
      <div class="actions">
        <button id="connect">Connect</button>
        <button id="camera" disabled>Start camera</button>
        <button id="control" disabled>Enable OS control</button>
      </div>
      <p id="message" class="message">Nothing is connected.</p>
    </section>

    <section class="preview panel">
      <video id="video" autoplay playsinline muted></video>
      <div class="hud">
        <span>Gesture: <strong id="gesture">none</strong></span>
        <span>Vision: <strong id="vision">off</strong></span>
        <span>Control: <strong id="controlState">off</strong></span>
      </div>
    </section>

    <p class="warning">OS control is disabled until you explicitly enable it. Never expose an unauthenticated companion to the public Internet.</p>
  </section>
`;

const status = document.querySelector<HTMLSpanElement>("#status")!;
const message = document.querySelector<HTMLParagraphElement>("#message")!;
const urlInput = document.querySelector<HTMLInputElement>("#url")!;
const tokenInput = document.querySelector<HTMLInputElement>("#token")!;
const connectButton = document.querySelector<HTMLButtonElement>("#connect")!;
const cameraButton = document.querySelector<HTMLButtonElement>("#camera")!;
const controlButton = document.querySelector<HTMLButtonElement>("#control")!;
const video = document.querySelector<HTMLVideoElement>("#video")!;
const gestureLabel = document.querySelector<HTMLElement>("#gesture")!;
const visionLabel = document.querySelector<HTMLElement>("#vision")!;
const controlLabel = document.querySelector<HTMLElement>("#controlState")!;

let socket: WebSocket | null = null;
let cameraStream: MediaStream | null = null;
let controlling = false;
let frameId = 0;
let lastVideoTime = -1;
const vision = new HandVision();
const gestures = new GestureEngine();

function setMessage(text: string): void {
  message.textContent = text;
}

function send(payload: object): boolean {
  if (!socket || socket.readyState !== WebSocket.OPEN) return false;
  socket.send(JSON.stringify(payload));
  return true;
}

function closeSocket(): void {
  socket?.close();
  socket = null;
  controlling = false;
  controlButton.disabled = true;
  controlButton.textContent = "Enable OS control";
  controlLabel.textContent = "off";
}

connectButton.addEventListener("click", () => {
  closeSocket();
  const url = urlInput.value.trim();
  const token = tokenInput.value;
  if (!url || !token) {
    setMessage("Enter the companion URL and pairing token.");
    return;
  }
  if (location.protocol === "https:" && url.startsWith("ws://")) {
    setMessage("An HTTPS site cannot use an insecure ws:// companion. Use wss:// for remote control.");
    return;
  }

  try {
    socket = new WebSocket(url);
  } catch {
    setMessage("The companion URL is invalid.");
    return;
  }

  status.textContent = "Connecting";
  socket.addEventListener("open", () => {
    send({ type: "auth", token });
  });
  socket.addEventListener("message", (event) => {
    try {
      const data = JSON.parse(event.data) as { ok?: boolean; type?: string; error?: string };
      if (data.type === "authenticated" && data.ok) {
        status.textContent = "Connected";
        controlButton.disabled = false;
        cameraButton.disabled = false;
        setMessage("Companion authenticated. Start the camera when ready.");
      } else if (!data.ok) {
        setMessage(data.error ?? "Companion rejected the request.");
      }
    } catch {
      setMessage("Received an invalid companion response.");
    }
  });
  socket.addEventListener("close", () => {
    status.textContent = "Disconnected";
    controlButton.disabled = true;
    cameraButton.disabled = true;
    controlling = false;
    controlLabel.textContent = "off";
    setMessage("Companion connection closed.");
  });
  socket.addEventListener("error", () => setMessage("Could not communicate with the companion."));
});

controlButton.addEventListener("click", () => {
  controlling = !controlling;
  controlButton.textContent = controlling ? "Disable OS control" : "Enable OS control";
  controlLabel.textContent = controlling ? "on" : "off";
});

cameraButton.addEventListener("click", async () => {
  if (cameraStream) {
    cameraStream.getTracks().forEach((track) => track.stop());
    cameraStream = null;
    video.srcObject = null;
    cancelAnimationFrame(frameId);
    vision.close();
    cameraButton.textContent = "Start camera";
    visionLabel.textContent = "off";
    setMessage("Camera stopped.");
    return;
  }

  try {
    cameraStream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: "user", width: { ideal: 1280 }, height: { ideal: 720 } },
      audio: false,
    });
    video.srcObject = cameraStream;
    await video.play();
    await vision.initialize();
    cameraButton.textContent = "Stop camera";
    visionLabel.textContent = "on";
    setMessage("Camera and hand tracking are running.");
    frameId = requestAnimationFrame(processFrame);
  } catch (error) {
    cameraStream?.getTracks().forEach((track) => track.stop());
    cameraStream = null;
    const detail = error instanceof Error ? error.message : "unknown camera error";
    setMessage(`Camera/vision initialization failed: ${detail}`);
  }
});

function processFrame(nowMs: number): void {
  if (!cameraStream || video.readyState < HTMLMediaElement.HAVE_CURRENT_DATA) {
    frameId = requestAnimationFrame(processFrame);
    return;
  }
  if (video.currentTime === lastVideoTime) {
    frameId = requestAnimationFrame(processFrame);
    return;
  }
  lastVideoTime = video.currentTime;

  try {
    const result = vision.detect(video, nowMs);
    const position = pointerPosition(result);
    const distance = pinchDistance(result);
    const gesture = distance !== null && distance < 0.055 ? "pinch" : "none";
    gestureLabel.textContent = gesture;
    const event = gestures.update(gesture, nowMs);

    if (controlling && position) send(moveCommand(position.x, position.y));
    if (controlling && event === "pinch") send({ command: "left_click" });
  } catch (error) {
    const detail = error instanceof Error ? error.message : "vision processing error";
    setMessage(`Vision processing stopped: ${detail}`);
    cancelAnimationFrame(frameId);
    return;
  }
  frameId = requestAnimationFrame(processFrame);
}

window.addEventListener("beforeunload", () => {
  cameraStream?.getTracks().forEach((track) => track.stop());
  vision.close();
  socket?.close();
});
