import api from "../../config/api.config";

export const getAllOrders = async (
  deliveryDate: string,
  timePreference: string,
  ordersLimit: number,
  offset: number
) => {
  try {
    const response = await api.get(`v1/orders/all`, {
      params: {
        deliveryDate: deliveryDate,
        timePreference: timePreference,
        limit: ordersLimit,
        offset: offset,
      },
    });
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
