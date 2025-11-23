import { routeConfig } from "../config/roles.config";

export const MODAL_CONFIG = {
  "/goods": {
    title: "Додати товар",
    component: "AddProductForm",
    allowedRoles: routeConfig.find(r => r.path === "/goods")?.allowedRoles || [],
  },
  "/clients": {
    title: "Додати клієнта",
    component: "AddClientForm",
    allowedRoles: routeConfig.find(r => r.path === "/clients")?.allowedRoles || [],
  },
  "/orders": {
    title: "Створити замовлення",
    component: "AddOrderForm",
    allowedRoles: routeConfig.find(r => r.path === "/orders")?.allowedRoles || [],
  },
  "/staff": {
    title: "Додати співробітника",
    component: "AddStaffForm",
    allowedRoles: routeConfig.find(r => r.path === "/staff")?.allowedRoles || [],
  },
};
