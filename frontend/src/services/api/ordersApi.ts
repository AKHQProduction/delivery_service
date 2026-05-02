import api from "../../config/api.config";

export interface OrderStatsItem {
  name: string;
  quantity: number;
  orders_sum: number;
}

export interface OrderStatsTimeSlot {
  time_slot: string;
  total: number;
  orders_sum: number;
}

export interface OrderStatsPaymentMethod {
  method: string;
  orders_sum: number;
}

export interface OrderStatsRecentOrder {
  order_id: string;
  date: string;
  time_slot: string;
  delivery_phone: string;
  delivery_address: {
    street?: string;
    house?: string;
    apartment?: string;
  };
  client_name: string;
  items: Array<{
    name: string;
    quantity: number;
    price_per_item: number;
  }>;
  payment_method: string;
  is_paid: boolean;
}

export interface OrderStats {
  total_orders: number;
  total_orders_sum: number;
  total_products_quantity: number;
  average_order_value: number;
  time_slot_stats: OrderStatsTimeSlot[];
  product_stats: OrderStatsItem[];
  category_stats: OrderStatsItem[];
  payment_method_stats: OrderStatsPaymentMethod[];
  recent_orders: OrderStatsRecentOrder[];
}

export interface OrderSummary {
  total_count: number;
  today_count: number;
  tomorrow_count: number;
  total_amount: number;
}

export const getAllOrders = async (
  client_name: string,
  start_date: string,
  end_date: string,
  time_preference: string,
  limit: number,
  offset: number,
) => {
  const params: Record<string, string | number> = {
    limit: limit,
    offset: offset,
    order: "ASC",
  };

  if (client_name) params.client_name = client_name;
  if (start_date) params.start_date = start_date;
  if (end_date) params.end_date = end_date;
  if (time_preference) params.delivery_start_time = time_preference;

  const response = await api.get(`v1/orders/all`, { params });
  return response.data;
};

export const getOrderSummary = async (
  client_name: string,
  start_date: string,
  end_date: string,
  time_preference: string,
): Promise<OrderSummary> => {
  const params: Record<string, string> = {};

  if (client_name) params.client_name = client_name;
  if (start_date) params.start_date = start_date;
  if (end_date) params.end_date = end_date;
  if (time_preference) params.delivery_start_time = time_preference;

  const response = await api.get(`v1/orders/summary`, { params });
  return response.data;
};

export const createOrder = async (orderData: unknown) => {
  const response = await api.post(`v1/orders`, orderData);
  return response.data;
};

export const updateOrder = async (orderId: string, orderData: unknown) => {
  const response = await api.patch(`v1/orders/${orderId}`, orderData);
  return response.data;
};

export const payOrderFromBalance = async (orderId: string) => {
  const response = await api.post(`v1/orders/${orderId}/pay-from-balance`);
  return response.data;
};

export const deleteOrderById = async (orderId: string) => {
  const response = await api.delete(`v1/orders/${orderId}`);
  return response.data;
};

export const getOrderById = async (orderId: string) => {
  const response = await api.get(`v1/orders/${orderId}`);
  return response.data;
};

export const generateOrdersPdfLink = async (
  deliveryDate: string,
  docType: "ORDER_LIST" | "STATISTICS",
  timeSlotId?: string,
  routingMode: "NONE" | "OPTIMIZED" = "NONE",
) => {
  const body: Record<string, string> = {
    delivery_date: deliveryDate,
    doc_type: docType,
    routing_mode: routingMode,
  };
  if (timeSlotId) {
    body.time_slot_id = timeSlotId;
  }
  const response = await api.post(`v1/orders/export/pdf/generate`, body);
  return response.data as { file_id: string; filename: string };
};

export const getOrderStats = async (start_date: string, end_date: string): Promise<OrderStats> => {
  const response = await api.get(`v1/orders/stats`, {
    params: {
      start_date,
      end_date,
    },
  });
  return response.data;
};
