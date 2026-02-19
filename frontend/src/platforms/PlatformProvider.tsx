import { createContext, useContext, useMemo } from "react";
import type { Platform } from "./types";
import { detectPlatform } from "./detect";
import { createWebPlatform } from "./web/WebPlatform";
import { createTelegramPlatform } from "./telegram/TelegramPlatform";

const PlatformContext = createContext<Platform | null>(null);

export const PlatformProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const platform = useMemo(() => {
    const type = detectPlatform();
    console.log(`%c[Platform] ${type}`, "font-size:20px;font-weight:bold;color:#2563eb");
    return type === "telegram" ? createTelegramPlatform() : createWebPlatform();
  }, []);

  return <PlatformContext.Provider value={platform}>{children}</PlatformContext.Provider>;
};

export const usePlatform = (): Platform => {
  const ctx = useContext(PlatformContext);
  if (!ctx) {
    throw new Error("usePlatform must be used within PlatformProvider");
  }
  return ctx;
};
