import type { TelegramWebAppData } from "../../types/telegram";

let sdk: TelegramWebAppData | null = null;
let initialized = false;

export const getTelegramSdk = (): TelegramWebAppData | null => {
  if (!initialized) {
    if (typeof window !== "undefined" && window.Telegram?.WebApp) {
      sdk = window.Telegram.WebApp as unknown as TelegramWebAppData;
      if (sdk.ready) {
        sdk.ready();
      }
    }
    initialized = true;
  }
  return sdk;
};

/** Returns the raw initData query string for Bearer auth, or undefined if not in TG WebApp */
export const getTelegramInitData = (): string | undefined => {
  const tg = getTelegramSdk();
  if (!tg) return undefined;
  const initData = tg.initData;
  return typeof initData === "string" && initData ? initData : undefined;
};
