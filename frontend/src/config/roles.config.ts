import { UserRole } from "../constants/roles";
import { ProductPage } from "../pages/ProductPage";
import { ClientsPage } from "../pages/ClientsPage";
import { OrdersPage } from "../pages/OrdersPage";
import { EmployeePage } from "../pages/EmployeePage";
import { OrdersStatsPage } from "../pages/OrderStatsPage";
import { MainPage } from "../pages/MainPage";
import { SettingsPage } from "../pages/SettingsPage";
import { ShopSettingsPage } from "../pages/ShopSettingsPage";
import goodsIcon from "../assets/icons/goods.svg";
import clientsIcon from "../assets/icons/client.svg";
import ordersIcon from "../assets/icons/order.svg";
import usersIcon from "../assets/icons/users.svg";
import statisticIcon from "../assets/icons/statistic-board-com.svg";
import menuIcon from "../assets/icons/menu.svg";
import settingsIcon from "../assets/icons/settings.svg";
import shopIcon from "../assets/icons/shop.svg";

export interface RouteConfig {
  path: string;
  label: string;
  icon: string;
  component: React.ComponentType;
  allowedRoles: UserRole[];
  showInNav?: boolean;
}

export const routeConfig: RouteConfig[] = [
  {
    path: "/",
    label: "Головна",
    icon: menuIcon,
    component: MainPage,
    allowedRoles: [UserRole.COURIER, UserRole.MANAGER, UserRole.OWNER],
  },

  {
    path: "/stats",
    label: "Статистика",
    icon: statisticIcon,
    component: OrdersStatsPage,
    allowedRoles: [UserRole.MANAGER, UserRole.OWNER],
    showInNav: false,
  },
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
    component: EmployeePage,
    allowedRoles: [UserRole.OWNER],
    showInNav: false,
  },
  {
    path: "/shop-settings",
    label: "Налаштування магазину",
    icon: shopIcon,
    component: ShopSettingsPage,
    allowedRoles: [UserRole.OWNER],
    showInNav: false,
  },
  {
    path: "/settings",
    label: "Налаштування",
    icon: settingsIcon,
    component: SettingsPage,
    allowedRoles: [UserRole.MANAGER, UserRole.OWNER],
    showInNav: false,
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
