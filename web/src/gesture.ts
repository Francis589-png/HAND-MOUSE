export type Gesture = "none" | "pinch" | "two_finger_pinch";

export interface GestureConfig {
  confirmationFrames: number;
  cooldownMs: number;
}

export class GestureEngine {
  private candidate: Gesture = "none";
  private candidateFrames = 0;
  private armed = true;
  private lastEventAt = -Infinity;

  constructor(private readonly config: GestureConfig = { confirmationFrames: 3, cooldownMs: 500 }) {
    if (!Number.isInteger(config.confirmationFrames) || config.confirmationFrames < 1) {
      throw new RangeError("confirmationFrames must be a positive integer");
    }
    if (!Number.isFinite(config.cooldownMs) || config.cooldownMs < 0) {
      throw new RangeError("cooldownMs must be a finite non-negative number");
    }
  }

  update(gesture: Gesture, nowMs: number): Gesture | null {
    if (!Number.isFinite(nowMs)) throw new RangeError("nowMs must be finite");
    if (gesture === "none") {
      this.candidate = "none";
      this.candidateFrames = 0;
      this.armed = true;
      return null;
    }

    if (gesture === this.candidate) this.candidateFrames += 1;
    else {
      this.candidate = gesture;
      this.candidateFrames = 1;
    }

    if (!this.armed || this.candidateFrames < this.config.confirmationFrames) return null;
    if (nowMs - this.lastEventAt < this.config.cooldownMs) return null;

    this.armed = false;
    this.lastEventAt = nowMs;
    return gesture;
  }
}
