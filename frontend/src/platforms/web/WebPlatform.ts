import type { Platform } from "../types";
import { webAuth } from "./webAuth";
import { webFiles } from "./webFiles";

export const createWebPlatform = (): Platform => ({
  type: "web",
  auth: webAuth,
  files: webFiles,
  features: { fullscreen: false },
  unauthorizedRedirect: "/login",
});
