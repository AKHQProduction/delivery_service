import { useState, useEffect } from "react";
import { getTelegramSdk } from "../../platforms/telegram/telegramSdk";
import { SettingsStorage } from "../../config/settings.config";
import { type AppSettings } from "../../types/settings";

export const useTGSettings = () => {
  const tg = getTelegramSdk();

  const [settings, setSettings] = useState<AppSettings>(() => SettingsStorage.load());

  useEffect(() => {
    if (!tg) return;

    if (settings.fullscreen && tg.requestFullscreen) {
      tg.requestFullscreen();
    }
  }, [tg, settings.fullscreen]);

  const updateSetting = <K extends keyof AppSettings>(key: K, value: AppSettings[K]) => {
    setSettings((prev) => {
      const updated = { ...prev, [key]: value };
      SettingsStorage.save(updated);
      return updated;
    });

    if (key === "fullscreen" && tg) {
      if (value && tg.requestFullscreen) {
        tg.requestFullscreen();
      } else if (!value && tg.exitFullscreen) {
        tg.exitFullscreen();
      }
    }
  };

  return {
    settings,
    updateSetting,
  };
};
