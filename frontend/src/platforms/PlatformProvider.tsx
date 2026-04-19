import { useMemo } from "react";
import type { ReactNode } from "react";
import { detectPlatform } from "./detect";
import { createWebPlatform } from "./web/WebPlatform";
import { createTelegramPlatform } from "./telegram/TelegramPlatform";
import { PlatformContext } from "./usePlatform";

export function PlatformProvider({ children }: { children: ReactNode }) {
  const platform = useMemo(() => {
    const type = detectPlatform();
    console.log(`%c[Platform] ${type}`, "font-size:20px;font-weight:bold;color:#2563eb");
    return type === "telegram" ? createTelegramPlatform() : createWebPlatform();
  }, []);

  return <PlatformContext.Provider value={platform}>{children}</PlatformContext.Provider>;
}
