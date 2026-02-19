import type { PlatformFiles } from "../types";

export const webFiles: PlatformFiles = {
  download(url: string, _filename: string) {
    window.open(url, "_blank");
  },

  openLink(url: string) {
    window.open(url, "_blank");
  },
};
