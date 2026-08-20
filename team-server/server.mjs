import { WebSocketServer } from "ws";

const PORT = Number(process.env.PORT || 8787);
const MAX_MESSAGE_BYTES = 64 * 1024;
const CODE_RE = /^HM-[A-Z2-9]{4}-[A-Z2-9]{4}$/;
const peers = new Map();

function send(ws, message) {
  if (ws.readyState === ws.OPEN) ws.send(JSON.stringify(message));
}

function validCode(code) {
  return typeof code === "string" && CODE_RE.test(code);
}

function detach(ws) {
  const code = ws.teamCode;
  if (!code) return;
  const entry = peers.get(code);
  if (!entry) return;
  entry.delete(ws);
  for (const peer of entry) send(peer, { type: "peer_left" });
  if (entry.size === 0) peers.delete(code);
  ws.teamCode = undefined;
}

const wss = new WebSocketServer({ port: PORT, maxPayload: MAX_MESSAGE_BYTES });

wss.on("connection", (ws) => {
  ws.on("message", (raw) => {
    let message;
    try { message = JSON.parse(raw.toString("utf8")); } catch { return send(ws, { type: "error", code: "INVALID_JSON" }); }

    if (message?.type === "join") {
      const code = typeof message.code === "string" ? message.code.trim().toUpperCase() : "";
      if (!validCode(code)) return send(ws, { type: "error", code: "INVALID_TEAM_CODE" });
      detach(ws);
      let entry = peers.get(code);
      if (!entry) { entry = new Set(); peers.set(code, entry); }
      if (entry.size >= 2) return send(ws, { type: "error", code: "TEAM_FULL" });
      entry.add(ws);
      ws.teamCode = code;
      send(ws, { type: "joined", code, peerCount: entry.size });
      for (const peer of entry) if (peer !== ws) send(peer, { type: "peer_joined" });
      return;
    }

    if (!ws.teamCode) return send(ws, { type: "error", code: "NOT_JOINED" });
    if (!["offer", "answer", "ice", "leave"].includes(message?.type)) return send(ws, { type: "error", code: "INVALID_SIGNAL" });
    const entry = peers.get(ws.teamCode);
    if (!entry) return;
    for (const peer of entry) if (peer !== ws) send(peer, message);
    if (message.type === "leave") detach(ws);
  });
  ws.on("close", () => detach(ws));
  ws.on("error", () => detach(ws));
});

console.log(`HAND-MOUSE Team signaling server listening on :${PORT}`);
