export type Command =
  | { command: "move"; x: number; y: number }
  | { command: "left_click" }
  | { command: "right_click" }
  | { command: "scroll"; amount: number };

export function assertNormalized(value: number, name: string): number {
  if (!Number.isFinite(value) || value < 0 || value > 1) {
    throw new RangeError(`${name} must be a finite number between 0 and 1`);
  }
  return value;
}

export function moveCommand(x: number, y: number): Command {
  return { command: "move", x: assertNormalized(x, "x"), y: assertNormalized(y, "y") };
}
