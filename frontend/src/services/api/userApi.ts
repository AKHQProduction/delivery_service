import api from "../../config/api.config";
import type { Shop, User } from "../../types/entities/user";

export interface UserShopData {
  user: User;
  shop: Shop | null;
  current_date?: string;
}

export const getUserShopData = async (): Promise<UserShopData> => {
  const response = await api.get(`v1/auth/me`);
  return response.data;
};

export const createNewShop = async (name: string) => {
  const response = await api.post(`v1/shop`, {
    name,
  });
  return response.data;
};

export const createInviteUserLink = async (role: string, full_name: string) => {
  const response = await api.post(`v1/links`, {
    role,
    full_name,
  });
  return response.data;
};
