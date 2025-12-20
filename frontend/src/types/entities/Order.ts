import { type Address } from "./Client";

export interface OrderItem {
  id: number;
  name: string;
  quantity: number;
  price_per_item: number;
}

export interface Order {
  order_id: string;
  client_id: string;
  client_name: string;
  date: string;
  time_preference: string;
  delivery_phone: string;
  delivery_address: Address;
  items: OrderItem[];
  comment?: string;
}
