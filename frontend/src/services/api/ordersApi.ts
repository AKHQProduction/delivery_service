import api from "../../config/api.config";

export const getAllOrders = async (
  clientName: string,
  customId: string,
  deliveryDate: string,
  timePreference: string,
  ordersLimit: number,
  offset: number
) => {
  try {
    const params: Record<string, string | number> = {
      limit: ordersLimit,
      offset: offset,
    };

    if (clientName) params.client_name = clientName;
    if (customId) params.custom_id = customId;
    if (deliveryDate) params.delivery_date = deliveryDate;
    if (timePreference) params.time_preference = timePreference;

    const response = await api.get(`v1/orders/all`, { params });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const createOrder = async (orderData: any) => {
  try {
    const response = await api.post(`v1/orders/`, orderData);
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

export const exportOrdersPdf = async (deliveryDate: string) => {
  try {
    const response = await api.get(`v1/orders/export/pdf`, {
      params: { delivery_date: deliveryDate },
      responseType: "blob",
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};
