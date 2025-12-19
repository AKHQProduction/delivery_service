import { type Product } from "./Product";
import { type Address } from "./Client";

export interface Order {
  client_id: string;
  client_name: string;
  comment?: string;
  date: string;
  delivery_address: Address;
  delivery_phone: string;
  items: Product;
  order_id: string;
  time_preference: string;
}
