export interface RoutePointCoordinates {
  latitude: number;
  longitude: number;
}

export interface RoutePoint {
  order_id: string;
  sequence: number;
  client_name: string;
  delivery_phone: string;
  address: string;
  coordinates: RoutePointCoordinates;
  items_summary: string;
  comment: string;
  payment_method: "CASH" | "BANK_TRANSFER" | "OTHER";
  total_price: number;
}

export interface RouteStats {
  total_orders: number;
  unique_addresses: number;
}

export interface RoutePlan {
  route_plan_id: string;
  delivery_date: string;
  time_slot: string;
  time_slot_id: string | null;
  points: RoutePoint[];
  unroutable_orders: RoutePoint[];
  stats: RouteStats;
}