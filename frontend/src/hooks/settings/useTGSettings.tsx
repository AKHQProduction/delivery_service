import { useState, useEffect } from "react";
import { useTelegram } from "../useTelegram";
import { SettingsStorage } from "../../config/settings.config";
import { type AppSettings } from "../../types/settings";

export const useTGSettings = () => {
  const { initDataTG } = useTelegram();

  const [settings, setSettings] = useState<AppSettings>(() => SettingsStorage.load());

  useEffect(() => {
    if (!initDataTG) return;

    if (settings.fullscreen && initDataTG.requestFullscreen) {
      initDataTG.requestFullscreen();
    }
  }, [initDataTG, settings.fullscreen]);

  const updateSetting = <K extends keyof AppSettings>(key: K, value: AppSettings[K]) => {
    setSettings((prev) => {
      const updated = { ...prev, [key]: value };
      SettingsStorage.save(updated);
      return updated;
    });

    if (key === "fullscreen" && initDataTG) {
      if (value && initDataTG.requestFullscreen) {
        initDataTG.requestFullscreen();
      } else if (!value && initDataTG.exitFullscreen) {
        initDataTG.exitFullscreen();
      }
    }
  };

  return {
    settings,
    updateSetting,
  };
};
