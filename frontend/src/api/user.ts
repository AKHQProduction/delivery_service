import api from "./setup";

export const getUser = async () => {
  try {
    const response = await api.get(`v1/users/me`);
    return response.data;
  } catch (error) {
    throw error;
  }
};
