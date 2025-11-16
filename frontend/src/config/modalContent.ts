export const MODAL_CONFIG = {
  "/products": {
    title: "Додати товар",
    component: "AddProductForm",
    height: "lg" as const,
  },
  "/clients": {
    title: "Додати клієнта",
    component: "AddClientForm",
    height: "lg" as const,
  },
  "/orders": {
    title: "Створити замовлення",
    component: "AddOrderForm",
    height: "full" as const,
  },
  "/staff": {
    title: "Додати співробітника",
    component: "AddStaffForm",
    height: "md" as const,
  },
};