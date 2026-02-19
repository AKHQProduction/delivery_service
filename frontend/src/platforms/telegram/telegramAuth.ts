import type { PlatformAuth } from "../types";
import { getTelegramInitData } from "./telegramSdk";

export const telegramAuth: PlatformAuth = {
  getHeaders(): Record<string, string> {
    const initData = getTelegramInitData();
    if (!initData) return {};
    return { Authorization: `Bearer ${initData}` };
  },

  onUnauthorized() {
    // TG WebApp: no redirect, the app stays open
  },
};
