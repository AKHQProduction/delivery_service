import type { Platform } from "../types";
import { telegramAuth } from "./telegramAuth";
import { telegramFiles } from "./telegramFiles";

export const createTelegramPlatform = (): Platform => ({
  type: "telegram",
  auth: telegramAuth,
  files: telegramFiles,
  features: { fullscreen: true },
  unauthorizedRedirect: "/",
});
