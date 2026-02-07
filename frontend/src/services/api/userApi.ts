import api from "../../config/api.config";

export const getUserShopData = async () => {
  const response = await api.get(`v1/users/me`);
  return response.data;
};

export const createInviteUserLink = async (role: string, full_name: string) => {
  const response = await api.post(`v1/links`, {
    role,
    full_name,
  });
  return response.data;
};
