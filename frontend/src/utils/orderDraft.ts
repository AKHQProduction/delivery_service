import { type Order } from "../types/entities/Order";

export interface RegularOrderDraft {
  client_id?: string;
  phone_id?: number;
  address_id?: number;
  delivery_date?: string;
  date?: string;
  time_slot_id?: string;
  payment_method?: string;
  comment?: string;
  note?: string;
  items?: Array<{
    id: number;
    product_id: string;
    name?: string;
    price_per_item?: number;
    quantity: number;
  }>;
}

export const buildRepeatOrderDraft = (
  order: Order,
  deliveryDate: string,
): RegularOrderDraft => ({
  client_id: order.client_id,
  delivery_date: deliveryDate,
  payment_method: order.payment_method,
  comment: order.comment || order.note || "",
  items: order.items
    .filter((item) => item.product_id)
    .map((item) => ({
      id: item.id,
      product_id: item.product_id as string,
      name: item.name,
      price_per_item: item.price_per_item,
      quantity: item.quantity,
    })),
});

export const getOrderItemsSummary = (order: Order) => {
  const quantity = order.items?.reduce((sum, item) => sum + item.quantity, 0);
  return `${quantity || 0} товарів`;
};
