import { FilesetResolver, HandLandmarker, type HandLandmarkerResult } from "@mediapipe/tasks-vision";

const MEDIAPIPE_VERSION = "0.10.35";
const WASM_ROOT = `https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@${MEDIAPIPE_VERSION}/wasm`;
const MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task";

export class HandVision {
  private landmarker: HandLandmarker | null = null;

  async initialize(): Promise<void> {
    const vision = await FilesetResolver.forVisionTasks(WASM_ROOT);
    this.landmarker = await HandLandmarker.createFromOptions(vision, {
      baseOptions: { modelAssetPath: MODEL_URL },
      runningMode: "VIDEO",
      numHands: 1,
      minHandDetectionConfidence: 0.6,
      minHandPresenceConfidence: 0.6,
      minTrackingConfidence: 0.6,
    });
  }

  detect(video: HTMLVideoElement, timestampMs: number): HandLandmarkerResult {
    if (!this.landmarker) throw new Error("Hand vision is not initialized");
    return this.landmarker.detectForVideo(video, timestampMs);
  }

  close(): void {
    this.landmarker?.close();
    this.landmarker = null;
  }
}

export function pinchDistance(result: HandLandmarkerResult): number | null {
  const hand = result.landmarks[0];
  if (!hand || hand.length < 9) return null;
  const thumb = hand[4];
  const index = hand[8];
  return Math.hypot(thumb.x - index.x, thumb.y - index.y);
}

export function pointerPosition(result: HandLandmarkerResult): { x: number; y: number } | null {
  const hand = result.landmarks[0];
  if (!hand || hand.length < 9) return null;
  return { x: Math.min(1, Math.max(0, 1 - hand[8].x)), y: Math.min(1, Math.max(0, hand[8].y)) };
}
