import api from "../../config/api.config";

//Time slots settings API calls
const dateToTimeString = (date: Date): string => {
  const hours = date.getHours().toString().padStart(2, "0");
  const minutes = date.getMinutes().toString().padStart(2, "0");
  const seconds = date.getSeconds().toString().padStart(2, "0");
  return `${hours}:${minutes}:${seconds}`;
};

export const createNewTimeSlot = async (
  start_time: Date,
  end_time: Date,
  label?: string,
) => {
  try {
    const response = await api.post(`v1/time-slots`, {
      start_time: dateToTimeString(start_time),
      end_time: dateToTimeString(end_time),
      label: label,
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const updateTimeSlot = async (
  time_slot_id: string,
  start_time: Date,
  end_time: Date,
  label?: string,
) => {
  try {
    const response = await api.patch(`v1/time-slots/${time_slot_id}`, {
      start_time: dateToTimeString(start_time),
      end_time: dateToTimeString(end_time),
      label: label,
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const deleteTimeSlot = async (time_slot_id: string) => {
  try {
    const response = await api.delete(`v1/time-slots/${time_slot_id}`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const getAllTimeSlots = async () => {
  try {
    const response = await api.get(`v1/time-slots/all`);
    return response.data;
  } catch (error) {
    throw error;
  }
};
