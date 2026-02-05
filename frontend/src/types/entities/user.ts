import { UserRole } from "../../constants/roles";

export interface User {
  user_id: string;
  full_name: string;
  role: UserRole;
}

export interface Shop {
  shop_id: string;
  city: string | null;
}
