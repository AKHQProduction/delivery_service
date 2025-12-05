import { UserRole } from "../constants/roles";
import { ProductPage } from "../pages/ProductPage";
import { ClientsPage } from "../pages/ClientsPage";
import { OrdersPage } from "../pages/OrdersPage";
import { StaffPage } from "../pages/StaffPage";
import goodsIcon from "../assets/icons/goods.svg";
import clientsIcon from "../assets/icons/client.svg";
import ordersIcon from "../assets/icons/order.svg";
import usersIcon from "../assets/icons/users.svg";

export interface RouteConfig {
  path: string;
  label: string;
  icon: string;
  component: React.ComponentType;
  allowedRoles: UserRole[];
}

export const routeConfig: RouteConfig[] = [
  {
    path: "/products",
    label: "Товари",
    icon: goodsIcon,
    component: ProductPage,
    allowedRoles: [UserRole.MANAGER, UserRole.OWNER],
  },
  {
    path: "/clients",
    label: "Клієнти",
    icon: clientsIcon,
    component: ClientsPage,
    allowedRoles: [UserRole.COURIER, UserRole.MANAGER, UserRole.OWNER],
  },
  {
    path: "/orders",
    label: "Замовлення",
    icon: ordersIcon,
    component: OrdersPage,
    allowedRoles: [UserRole.COURIER, UserRole.MANAGER, UserRole.OWNER],
  },
  {
    path: "/staff",
    label: "Персонал",
    icon: usersIcon,
    component: StaffPage,
    allowedRoles: [UserRole.OWNER],
  },
];

export const getRoutesForRole = (role: UserRole): RouteConfig[] => {
  return routeConfig.filter((route) => route.allowedRoles.includes(role));
};

export const hasAccessToPath = (role: UserRole, path: string): boolean => {
  const route = routeConfig.find((r) => r.path === path);
  return route ? route.allowedRoles.includes(role) : false;
};

export const getDefaultRouteForRole = (role: UserRole): string => {
  const routes = getRoutesForRole(role);
  return routes[0]?.path || "/";
};
