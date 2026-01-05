declare global {
  interface Window {
    Telegram: {
      WebApp: {
        showPopup(
          arg0: { message: string; buttons: { type: string; text: string }[] },
          arg1?: () => void
        ): unknown;
        showAlert(arg0: string, arg1: () => void): unknown;
        showConfirm(arg0: string, arg1: (confirmed: any) => void): unknown;
        onEvent(arg0: string, handleGoBack: () => void): unknown;
        offEvent(arg0: string, handleGoBack: () => void): unknown;
        initDataUnsafe: any;
        BackButton: any;
        openLink(arg0: string): unknown;
        platform: string;
        openTelegramLink(arg0: string): unknown;
      };
    };
  }
}

export interface TelegramWebAppData {
  query_id?: string;
  user?: Record<string, any>;
  auth_date?: number;
  hash?: string;
  [key: string]: any;
  showConfirm: any;
}
