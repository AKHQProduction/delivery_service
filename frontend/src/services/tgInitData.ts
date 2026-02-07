import { type TelegramWebAppData } from "../types/telegram";

const initData = (): TelegramWebAppData | null => {
  let data: TelegramWebAppData | null = null;

  const checkTelegramData = () => {
    if (window.Telegram?.WebApp) {
      data = window.Telegram.WebApp;
    }
  };

  if (typeof window !== "undefined" && window.Telegram?.WebApp) {
    checkTelegramData();
  } else {
    const interval = setInterval(() => {
      if (window.Telegram?.WebApp) {
        checkTelegramData();
        clearInterval(interval);
      }
    }, 1);
    clearInterval(interval);
    data = null;
  }
  console.log("DATA:", data);
  return data;
};

const initDataTG = initData();

export default initDataTG;
