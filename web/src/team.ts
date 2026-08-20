export type TeamPermission = "screen" | "camera" | "hand" | "control";

export type TeamRequest = {
  type: "team_request";
  code: string;
  requesterName: string;
};

export type TeamResponse = {
  type: "team_response";
  accepted: boolean;
  permissions: TeamPermission[];
};

const CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";

export function createTeamCode(random: () => number = Math.random): string {
  let value = "HM-";
  for (let i = 0; i < 8; i += 1) {
    value += CODE_ALPHABET[Math.floor(random() * CODE_ALPHABET.length)];
    if (i === 3) value += "-";
  }
  return value;
}

export function normalizeTeamCode(value: string): string {
  return value.trim().toUpperCase();
}

export function validTeamCode(value: string): boolean {
  return /^HM-[A-Z2-9]{4}-[A-Z2-9]{4}$/.test(normalizeTeamCode(value));
}

export function canUsePermission(
  granted: readonly TeamPermission[],
  permission: TeamPermission,
): boolean {
  return granted.includes(permission);
}
