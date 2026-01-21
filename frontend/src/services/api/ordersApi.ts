import api from "../../config/api.config";

export const getAllOrders = async (
  client_name: string,
  custom_id: string,
  start_date: string,
  end_date: string,
  time_preference: string,
  limit: number,
  offset: number,
) => {
  try {
    const params: Record<string, string | number> = {
      limit: limit,
      offset: offset,
    };

    if (client_name) params.client_name = client_name;
    if (custom_id) params.custom_id = custom_id;
    if (start_date) params.start_date = start_date;
    if (end_date) params.end_dfate = end_date;
    if (time_preference) params.time_preference = time_preference;

    const response = await api.get(`v1/orders/all`, { params });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const createOrder = async (orderData: any) => {
  try {
    const response = await api.post(`v1/orders`, orderData);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const updateOrder = async (orderId: string, orderData: any) => {
  try {
    const response = await api.patch(`v1/orders/${orderId}`, orderData);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const deleteOrderById = async (orderId: string) => {
  try {
    const response = await api.delete(`v1/orders/${orderId}`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const getOrderById = async (orderId: string) => {
  try {
    const response = await api.get(`v1/orders/${orderId}`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const generateOrdersPdfLink = async (deliveryDate: string) => {
  try {
    const response = await api.post(`v1/orders/export/pdf/generate`, null, {
      params: { delivery_date: deliveryDate },
    });
    return response.data as { file_id: string; filename: string };
  } catch (error) {
    throw error;
  }
};

export const getOrderStats = async (start_date: string, end_date: string) => {
  try {
    const response = await api.get(`/api/v1/orders/stats`, {
      params: {
        start_date,
        end_date,
      },
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};
