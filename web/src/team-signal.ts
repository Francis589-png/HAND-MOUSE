export type TeamSignal =
  | { type: "joined"; code: string; peerCount: number }
  | { type: "peer_joined" }
  | { type: "peer_left" }
  | { type: "offer"; sdp: RTCSessionDescriptionInit }
  | { type: "answer"; sdp: RTCSessionDescriptionInit }
  | { type: "ice"; candidate: RTCIceCandidateInit }
  | { type: "team_request"; requesterName: string }
  | { type: "team_response"; accepted: boolean }
  | { type: "error"; code: string };

export class TeamSignalingClient {
  private readonly socket: WebSocket;
  private readonly listeners = new Set<(message: TeamSignal) => void>();

  constructor(url: string) {
    if (!/^wss?:\/\//.test(url)) throw new Error("Signaling URL must use ws:// or wss://");
    this.socket = new WebSocket(url);
    this.socket.onmessage = (event) => {
      try {
        const message = JSON.parse(String(event.data)) as TeamSignal;
        this.listeners.forEach((listener) => listener(message));
      } catch {
        // Ignore malformed signaling messages.
      }
    };
  }

  onMessage(listener: (message: TeamSignal) => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  async waitUntilOpen(timeoutMs = 5000): Promise<void> {
    if (this.socket.readyState === WebSocket.OPEN) return;
    await new Promise<void>((resolve, reject) => {
      const timer = window.setTimeout(() => reject(new Error("Signaling connection timed out")), timeoutMs);
      const cleanup = () => window.clearTimeout(timer);
      this.socket.addEventListener("open", () => { cleanup(); resolve(); }, { once: true });
      this.socket.addEventListener("error", () => { cleanup(); reject(new Error("Signaling connection failed")); }, { once: true });
    });
  }

  async join(code: string): Promise<void> {
    await this.waitUntilOpen();
    this.send({ type: "join", code });
  }

  send(message: object): void {
    if (this.socket.readyState !== WebSocket.OPEN) throw new Error("Signaling connection is not open");
    this.socket.send(JSON.stringify(message));
  }

  close(): void { this.socket.close(); }
}
