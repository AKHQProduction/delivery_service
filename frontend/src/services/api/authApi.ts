import api from "../../config/api.config";

export interface TelegramLoginData {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  photo_url?: string;
  auth_date: number;
  hash: string;
}

export const loginViaTelegram = async (data: TelegramLoginData): Promise<void> => {
  await api.post("v1/auth/telegram", data);
};

export const logout = async (): Promise<void> => {
  await api.post("v1/auth/logout");
};

export const checkSession = async (): Promise<{ user_id: string }> => {
  const response = await api.get("v1/auth/check");
  return response.data;
};
