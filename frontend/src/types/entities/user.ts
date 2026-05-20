import { UserRole } from "../../constants/roles";

export interface User {
  user_id: string;
  full_name: string;
  role: UserRole;
}

export type RepeatOrderMode = "CONFIRMATION_REQUIRED" | "CREATE_REGULAR_ORDER";

export interface Shop {
  shop_id: string;
  city: string | null;
  street: string | null;
  house: string | null;
  repeat_order_mode?: RepeatOrderMode | null;
}
