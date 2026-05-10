import { type Address } from "./Client";

export interface OrderItem {
  id: number;
  name: string;
  quantity: number;
  price_per_item: number;
  product_id: string | null;
}

export interface Order {
  order_id: string;
  client_id: string;
  client_name: string;
  date: string;
  time_preference: string;
  time_slot?: string;
  delivery_phone: string;
  delivery_address: Address;
  items: OrderItem[];
  payment_method?: string;
  comment?: string;
  note?: string;
  is_paid: boolean;
  recurring_order_id?: string | null;
}
