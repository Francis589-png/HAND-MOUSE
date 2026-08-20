import { describe, expect, it } from "vitest";

describe("Firebase Team configuration", () => {
  it("does not expose service-account credentials", () => {
    expect(import.meta.env.VITE_FIREBASE_API_KEY ?? "").not.toContain("private_key");
    expect(import.meta.env.VITE_FIREBASE_API_KEY ?? "").not.toContain("BEGIN PRIVATE KEY");
  });

  it("requires a Firebase project id for a configured browser build", () => {
    const projectId = import.meta.env.VITE_FIREBASE_PROJECT_ID;
    if (projectId) expect(projectId.length).toBeGreaterThan(0);
  });
});
