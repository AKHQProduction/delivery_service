import type { PlatformFiles } from "../types";

export const telegramFiles: PlatformFiles = {
  download(url: string, filename: string) {
    try {
      if (window.Telegram?.WebApp?.downloadFile) {
        window.Telegram.WebApp.downloadFile({ url, file_name: filename });
        return;
      }
    } catch {
      // downloadFile exists but unsupported in this WebApp version — fall through
    }

    if (window.Telegram?.WebApp?.openLink) {
      window.Telegram.WebApp.openLink(url);
    } else {
      window.open(url, "_blank");
    }
  },

  openLink(url: string) {
    if (window.Telegram?.WebApp?.openLink) {
      window.Telegram.WebApp.openLink(url);
    } else {
      window.open(url, "_blank");
    }
  },
};
