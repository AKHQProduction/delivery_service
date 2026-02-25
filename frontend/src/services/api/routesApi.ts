import api from "../../config/api.config";

export const getRoutes = async (delivery_date: string, time_slot_id: string | null) => {
  const params: Record<string, string | null> = {
    delivery_date: delivery_date,
    time_slot_id: time_slot_id,
  };
  const response = await api.get(`v1/route`, { params });
  return response.data;
};

export const reorderRoute = async (
  delivery_date: string,
  order_id: string,
  new_position: number,
  time_slot_id: string | null,
) => {
  const body = {
    delivery_date,
    order_id,
    new_position,
    time_slot_id,
  };
  const response = await api.patch(`v1/route`, {
    ...body,
  });
  return response.data;
};

export const updateOrderCoordinates = async (order_id: string, latitude: number, longitude: number) => {
  const response = await api.patch(`v1/route/orders/${order_id}/coordinates`, {
    latitude,
    longitude,
  });
  return response.data;
}