import { UserRole } from "./roles";

export interface User {
  user_id: string;
  role: UserRole;
}
