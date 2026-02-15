import api from "../../config/api.config";

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
  if (time_preference) params.time_preference = time_preference;

  const response = await api.get(`v1/orders/all`, { params });
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
  routingMode: "NONE" | "ROUNDTRIP" | "ONE_WAY" = "NONE",
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

export const getOrderStats = async (start_date: string, end_date: string) => {
  const response = await api.get(`/api/v1/orders/stats`, {
    params: {
      start_date,
      end_date,
    },
  });
  return response.data;
};
