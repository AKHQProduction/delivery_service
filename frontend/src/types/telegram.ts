declare global {
  interface Window {
    onTelegramAuth?: (user: {
      id: number;
      first_name: string;
      last_name?: string;
      username?: string;
      photo_url?: string;
      auth_date: number;
      hash: string;
    }) => void;
    Telegram: {
      WebApp: {
        showPopup(
          arg0: { message: string; buttons: { type: string; text: string }[] },
          arg1?: () => void,
        ): unknown;
        showAlert(arg0: string, arg1: () => void): unknown;
        showConfirm(arg0: string, arg1: (confirmed: boolean) => void): unknown;
        onEvent(arg0: string, handleGoBack: () => void): unknown;
        offEvent(arg0: string, handleGoBack: () => void): unknown;
        initDataUnsafe: Record<string, unknown>;
        BackButton: {
          show: () => void;
          hide: () => void;
          onClick: (callback: () => void) => void;
          offClick: (callback: () => void) => void;
          isVisible: boolean;
        };
        openLink(arg0: string): unknown;
        platform: string;
        openTelegramLink(arg0: string): unknown;
        downloadFile(arg0: { url: string; file_name: string }): unknown;
      };
    };
  }
}

export interface TelegramWebAppData {
  query_id?: string;
  user?: Record<string, unknown>;
  auth_date?: number;
  hash?: string;
  showConfirm?: (message: string, callback: (confirmed: boolean) => void) => void;
  ready?: () => void;
  requestFullscreen?: () => void;
  exitFullscreen?: () => void;
  openTelegramLink?: (url: string) => void;
  SettingsButton?: {
    show: () => void;
    hide: () => void;
    onClick: (callback: () => void) => void;
    offClick: (callback: () => void) => void;
  };
  [key: string]: unknown;
}
