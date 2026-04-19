import { createContext, useContext } from "react";
import type { Platform } from "./types";

export const PlatformContext = createContext<Platform | null>(null);

export function usePlatform(): Platform {
  const ctx = useContext(PlatformContext);
  if (!ctx) {
    throw new Error("usePlatform must be used within PlatformProvider");
  }
  return ctx;
}
