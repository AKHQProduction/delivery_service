export type PlatformType = "web" | "telegram";

export interface PlatformAuth {
  getHeaders(): Record<string, string>;
  onUnauthorized(): void;
}

export interface PlatformFiles {
  download(url: string, filename: string): void;
  openLink(url: string): void;
}

export interface PlatformFeatures {
  fullscreen: boolean;
}

export interface Platform {
  type: PlatformType;
  auth: PlatformAuth;
  files: PlatformFiles;
  features: PlatformFeatures;
  unauthorizedRedirect: string;
}
