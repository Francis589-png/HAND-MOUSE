import { getApps, initializeApp } from "firebase/app";
import { getAuth, signInAnonymously } from "firebase/auth";
import { getDatabase, onChildAdded, onDisconnect, onValue, push, ref, remove, set } from "firebase/database";

export type TeamSignal =
  | { type: "offer"; sdp: RTCSessionDescriptionInit }
  | { type: "answer"; sdp: RTCSessionDescriptionInit }
  | { type: "ice"; candidate: RTCIceCandidateInit };

export type TeamRequest = { requesterId: string; requesterName: string; createdAt: number };

const app = getApps()[0] ?? initializeApp({
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  databaseURL: import.meta.env.VITE_FIREBASE_DATABASE_URL,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
});

const auth = getAuth(app);
const database = getDatabase(app);

export async function ensureTeamAuth(): Promise<string> {
  if (auth.currentUser) return auth.currentUser.uid;
  const credential = await signInAnonymously(auth);
  return credential.user.uid;
}

function teamRef(code: string, child = ""): ReturnType<typeof ref> {
  return ref(database, `teams/${code}${child ? `/${child}` : ""}`);
}

export async function createTeam(code: string, ownerName: string): Promise<string> {
  const uid = await ensureTeamAuth();
  await set(teamRef(code), { ownerId: uid, ownerName, createdAt: Date.now(), members: { [uid]: { name: ownerName, joinedAt: Date.now() } } });
  onDisconnect(teamRef(code)).remove();
  return uid;
}

export async function requestTeam(code: string, requesterName: string): Promise<string> {
  const uid = await ensureTeamAuth();
  await set(teamRef(code, `requests/${uid}`), { requesterId: uid, requesterName, createdAt: Date.now() });
  onDisconnect(teamRef(code, `requests/${uid}`)).remove();
  return uid;
}

export function listenToRequests(code: string, callback: (request: TeamRequest | null) => void): () => void {
  return onChildAdded(teamRef(code, "requests"), (snapshot) => callback(snapshot.val() as TeamRequest));
}

export async function setTeamAccepted(code: string, peerId: string, accepted: boolean, peerName?: string): Promise<void> {
  const uid = await ensureTeamAuth();
  if (accepted) {
    await set(teamRef(code, `members/${peerId}`), { name: peerName ?? "Team member", joinedAt: Date.now() });
  }
  await set(teamRef(code, `responses/${peerId}`), { accepted, at: Date.now(), ownerId: uid });
  if (!accepted) await remove(teamRef(code, `requests/${peerId}`));
}

export function listenToResponse(code: string, peerId: string, callback: (accepted: boolean | null) => void): () => void {
  return onValue(teamRef(code, `responses/${peerId}`), (snapshot) => {
    const value = snapshot.val() as { accepted?: boolean } | null;
    callback(typeof value?.accepted === "boolean" ? value.accepted : null);
  });
}

export async function sendSignal(code: string, peerId: string, signal: TeamSignal): Promise<void> {
  const uid = await ensureTeamAuth();
  await push(teamRef(code, `signals/${peerId}/${uid}`), { ...signal, at: Date.now() });
}

export function listenToSignals(code: string, peerId: string, callback: (signal: TeamSignal) => void): () => void {
  return onChildAdded(teamRef(code, `signals/${peerId}`), (senderSnapshot) => {
    onChildAdded(senderSnapshot.ref, (messageSnapshot) => callback(messageSnapshot.val() as TeamSignal));
  });
}

export async function leaveTeam(code: string): Promise<void> {
  await remove(teamRef(code));
}
