import { UserRole } from "../types/roles";
import goodsIcon from "../assets/icons/goods.svg";
import clientsIcon from "../assets/icons/client.svg";
import ordersIcon from "../assets/icons/order.svg";
import usersIcon from "../assets/icons/users.svg";

export const roleButtons: Partial<
  Record<UserRole, { label: string; path: string; icon: string }[]>
> = {
  [UserRole.COURIER]: [
    { label: "Клієнти", path: "/clients", icon: clientsIcon },
    { label: "Замовлення", path: "/orders", icon: ordersIcon },
  ],
  [UserRole.MANAGER]: [
    { label: "Товари", path: "/goods", icon: goodsIcon },
    { label: "Клієнти", path: "/clients", icon: clientsIcon },
    { label: "Замовлення", path: "/orders", icon: ordersIcon },
  ],
  [UserRole.OWNER]: [
    { label: "Товари", path: "/goods", icon: goodsIcon },
    { label: "Клієнти", path: "/clients", icon: clientsIcon },
    { label: "Замовлення", path: "/orders", icon: ordersIcon },
    { label: "Персонал", path: "/staff", icon: usersIcon },
  ],
};
