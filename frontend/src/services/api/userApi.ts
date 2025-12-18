import api from "../../config/api.config";

export const getUser = async () => {
  try {
    const response = await api.get(`v1/users/me`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const createInviteUserLink = async (role: string, full_name: string) => {
  try {
    const response = await api.post(`v1/links`, {
      role,
      full_name,
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};
