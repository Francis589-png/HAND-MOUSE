export type SignalMessage =
  | { type: "offer"; sdp: RTCSessionDescriptionInit }
  | { type: "answer"; sdp: RTCSessionDescriptionInit }
  | { type: "ice"; candidate: RTCIceCandidateInit }
  | { type: "leave" };

export type TeamPeerState = "new" | "connecting" | "connected" | "closed";

export type TeamPeerOptions = {
  onSignal: (message: SignalMessage) => void;
  onState?: (state: TeamPeerState) => void;
  onData?: (data: unknown) => void;
  rtcConfiguration?: RTCConfiguration;
};

export class TeamPeer {
  private readonly pc: RTCPeerConnection;
  private readonly onSignal: (message: SignalMessage) => void;
  private readonly onState?: (state: TeamPeerState) => void;
  private readonly onData?: (data: unknown) => void;
  private channel?: RTCDataChannel;
  private pendingCandidates: RTCIceCandidateInit[] = [];
  private remoteDescriptionSet = false;

  constructor(options: TeamPeerOptions) {
    this.onSignal = options.onSignal;
    this.onState = options.onState;
    this.onData = options.onData;
    this.pc = new RTCPeerConnection(options.rtcConfiguration ?? {});

    this.pc.onicecandidate = (event) => {
      if (event.candidate) {
        this.onSignal({ type: "ice", candidate: event.candidate.toJSON() });
      }
    };
    this.pc.onconnectionstatechange = () => {
      const state = this.pc.connectionState;
      this.onState?.(
        state === "connected" ? "connected" :
        state === "closed" ? "closed" :
        state === "failed" ? "closed" : "connecting",
      );
    };
    this.pc.ondatachannel = (event) => this.attachDataChannel(event.channel);
  }

  private attachDataChannel(channel: RTCDataChannel): void {
    this.channel = channel;
    channel.onmessage = (event) => {
      try {
        this.onData?.(JSON.parse(String(event.data)));
      } catch {
        // Ignore malformed peer data; protocol consumers remain isolated.
      }
    };
  }

  createDataChannel(label = "team"): RTCDataChannel {
    const channel = this.pc.createDataChannel(label, { ordered: true });
    this.attachDataChannel(channel);
    return channel;
  }

  async createOffer(): Promise<void> {
    this.onState?.("connecting");
    const offer = await this.pc.createOffer();
    await this.pc.setLocalDescription(offer);
    this.onSignal({ type: "offer", sdp: offer });
  }

  async handleSignal(message: SignalMessage): Promise<void> {
    if (message.type === "offer") {
      this.onState?.("connecting");
      await this.pc.setRemoteDescription(message.sdp);
      this.remoteDescriptionSet = true;
      await this.flushCandidates();
      const answer = await this.pc.createAnswer();
      await this.pc.setLocalDescription(answer);
      this.onSignal({ type: "answer", sdp: answer });
      return;
    }

    if (message.type === "answer") {
      await this.pc.setRemoteDescription(message.sdp);
      this.remoteDescriptionSet = true;
      await this.flushCandidates();
      return;
    }

    if (message.type === "ice") {
      if (!this.remoteDescriptionSet) {
        this.pendingCandidates.push(message.candidate);
        return;
      }
      await this.pc.addIceCandidate(message.candidate);
      return;
    }

    this.close();
  }

  send(data: unknown): void {
    if (!this.channel || this.channel.readyState !== "open") {
      throw new Error("Team data channel is not open");
    }
    this.channel.send(JSON.stringify(data));
  }

  close(): void {
    this.channel?.close();
    this.pc.close();
    this.onState?.("closed");
  }

  private async flushCandidates(): Promise<void> {
    const candidates = this.pendingCandidates.splice(0);
    for (const candidate of candidates) {
      await this.pc.addIceCandidate(candidate);
    }
  }
}
