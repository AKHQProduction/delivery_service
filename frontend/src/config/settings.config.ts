import { DEFAULT_SETTINGS, type AppSettings } from "../types/settings";

const STORAGE_KEY = "settings";

export const SettingsStorage = {
  load(): AppSettings {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      return raw
        ? { ...DEFAULT_SETTINGS, ...JSON.parse(raw) }
        : DEFAULT_SETTINGS;
    } catch {
      return DEFAULT_SETTINGS;
    }
  },

  save(settings: AppSettings) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
  },
};
