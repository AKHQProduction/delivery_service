export const UserRole = {
  OWNER: "OWNER",
  MANAGER: "MANAGER",
  COURIER: "COURIER",
} as const;

export type UserRole = (typeof UserRole)[keyof typeof UserRole];
