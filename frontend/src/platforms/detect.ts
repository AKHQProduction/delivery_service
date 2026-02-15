import type { PlatformType } from "./types";

export const detectPlatform = (): PlatformType => {
  // initDataUnsafe.user only exists inside the actual Telegram Mini App,
  // not when telegram-widget.js is loaded in a regular browser
  if (typeof window !== "undefined" && window.Telegram?.WebApp?.initDataUnsafe?.user) {
    return "telegram";
  }
  return "web";
};
