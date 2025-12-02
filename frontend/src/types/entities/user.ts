import { UserRole } from "../../constants/roles";

export interface User {
  user_id: string;
  role: UserRole;
}
