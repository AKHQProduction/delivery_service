export type RecurringOrderStatus = "ACTIVE" | "PAUSED";
export type ScheduleType = "WEEKLY" | "MONTHLY_BY_DAY";

export interface RecurringOrderItem {
  product_id: string;
  product_name: string;
  quantity: number;
  current_price: number;
}

export interface RecurringOrder {
  recurring_order_id: string;
  client_id: string;
  client_name: string;
  phone_id: number | null;
  phone_number: string | null;
  address_id: number | null;
  address_summary: string | null;
  time_slot_id: string | null;
  time_slot_label?: string | null;
  delivery_start_time: string | null;
  delivery_end_time: string | null;
  schedule_type: ScheduleType;
  weekdays: number[] | null;
  month_days: number[] | null;
  items_count: number;
  status: RecurringOrderStatus;
}

export interface RecurringOrderDetail extends RecurringOrder {
  payment_method: string;
  comment?: string | null;
  items: RecurringOrderItem[];
}

export interface CreateRecurringOrderPayload {
  client_id: string;
  address_id: number;
  phone_id: number;
  time_slot_id: string;
  items: Array<{ product_id: string; quantity: number }>;
  payment_method: string;
  comment?: string | null;
  schedule_type: ScheduleType;
  weekdays?: number[] | null;
  month_days?: number[] | null;
}

export type UpdateRecurringOrderPayload = Omit<CreateRecurringOrderPayload, "client_id">;

export interface RunRecurringOrderPayload {
  include_today?: boolean;
  activate?: boolean;
}

export interface RunRecurringOrderResult {
  created_dates: string[];
  already_scheduled_dates: string[];
  cancelled_dates: string[];
  paused: boolean;
}
