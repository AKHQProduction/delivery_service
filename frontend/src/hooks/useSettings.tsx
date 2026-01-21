import { useState, useEffect } from "react";
import { useTelegram } from "./useTelegram";
import { SettingsStorage } from "../config/settings.config";
import { type AppSettings } from "../types/settings";

export const useSettings = () => {
  const { initDataTG } = useTelegram();

  const [settings, setSettings] = useState<AppSettings>(() =>
    SettingsStorage.load(),
  );

  useEffect(() => {
    if (!initDataTG) return;

    if (settings.fullscreen) {
      initDataTG.requestFullscreen();
    }
  }, [initDataTG]);

  const updateSetting = <K extends keyof AppSettings>(
    key: K,
    value: AppSettings[K],
  ) => {
    setSettings((prev) => {
      const updated = { ...prev, [key]: value };
      SettingsStorage.save(updated);
      return updated;
    });

    if (key === "fullscreen" && initDataTG) {
      value ? initDataTG.requestFullscreen() : initDataTG.exitFullscreen();
    }
  };

  return {
    settings,
    updateSetting,
  };
};
