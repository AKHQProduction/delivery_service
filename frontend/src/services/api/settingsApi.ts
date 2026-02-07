import api from "../../config/api.config";

//Time slots settings API calls
const dateToTimeString = (date: Date): string => {
  const hours = date.getHours().toString().padStart(2, "0");
  const minutes = date.getMinutes().toString().padStart(2, "0");
  const seconds = date.getSeconds().toString().padStart(2, "0");
  return `${hours}:${minutes}:${seconds}`;
};

export const createNewTimeSlot = async (start_time: Date, end_time: Date, label?: string) => {
  const response = await api.post(`v1/time-slots`, {
    start_time: dateToTimeString(start_time),
    end_time: dateToTimeString(end_time),
    label: label,
  });
  return response.data;
};

export const updateTimeSlot = async (
  time_slot_id: string,
  start_time: Date,
  end_time: Date,
  label?: string,
) => {
  const response = await api.patch(`v1/time-slots/${time_slot_id}`, {
    start_time: dateToTimeString(start_time),
    end_time: dateToTimeString(end_time),
    label: label,
  });
  return response.data;
};

export const deleteTimeSlot = async (time_slot_id: string) => {
  const response = await api.delete(`v1/time-slots/${time_slot_id}`);
  return response.data;
};

export const getAllTimeSlots = async () => {
  const response = await api.get(`v1/time-slots/all`);
  return response.data;
};

// Shop settings API calls
export interface ShopAddressPayload {
  address: {
    city: string;
    street: string;
    house: string;
    coordinates?: {
      latitude: number;
      longitude: number;
    };
  };
}

export const updateShopAddress = async (payload: ShopAddressPayload) => {
  const response = await api.patch(`v1/shop`, payload);
  return response.data;
};

export const createDistrict = async (name: string) => {
  const response = await api.post(`v1/districts`, { name });
  return response.data;
};

export const updateDistrict = async (district_id: string, name: string) => {
  const response = await api.patch(`v1/districts/${district_id}`, { name });
  return response.data;
};

export const deleteDistrict = async (district_id: string) => {
  const response = await api.delete(`v1/districts/${district_id}`);
  return response.data;
};

export const getAllDistricts = async () => {
  const response = await api.get(`v1/districts/all`);
  return response.data;
};
