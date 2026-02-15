import type { PlatformAuth } from "../types";
import { useUserShopStore } from "../../context/useUserShopStore";

export const webAuth: PlatformAuth = {
  getHeaders() {
    // Web uses cookies (withCredentials: true), no extra headers needed
    return {};
  },

  onUnauthorized() {
    const store = useUserShopStore.getState();
    if (store.authStatus === "authenticated") {
      store.logout();
      window.location.href = "/login";
    }
  },
};
