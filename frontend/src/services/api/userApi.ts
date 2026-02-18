import api from "../../config/api.config";

export const getUserShopData = async () => {
  const response = await api.get(`v1/auth/me`);
  return response.data;
};

export const createNewShop = async (name: string, owner_full_name: string) => {
  const response = await api.post(`v1/shop`, {
    name: name,
    owner_full_name: owner_full_name,
  });
  return response.data;
}

export const createInviteUserLink = async (role: string, full_name: string) => {
  const response = await api.post(`v1/links`, {
    role,
    full_name,
  });
  return response.data;
};
