import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { User, Shop } from "../types/entities/user";
import { UserRole } from "../constants/roles";

type AuthStatus = "idle" | "loading" | "authenticated" | "unauthenticated";

interface UserShopStore {
  user: User | null;
  shop: Shop | null;
  currentDate: string | null;
  authStatus: AuthStatus;

  setUser: (u: User | null) => void;
  setShop: (s: Shop | null) => void;
  setUserAndShop: (user: User | null, shop: Shop | null) => void;
  setCurrentDate: (currentDate: string | null) => void;
  clear: () => void;
  setAuthStatus: (status: AuthStatus) => void;
  logout: () => void;

  hasRole: (role: UserRole) => boolean;
  hasAnyRole: (roles: UserRole[]) => boolean;
}

export const useUserShopStore = create(
  persist<UserShopStore>(
    (set, get) => ({
      user: null,
      shop: null,
      currentDate: null,
      authStatus: "idle" as AuthStatus,

      setUser: (u) => set({ user: u }),
      setShop: (s) => set({ shop: s }),
      setUserAndShop: (user, shop) => set({ user, shop }),
      setCurrentDate: (currentDate) => set({ currentDate }),
      clear: () => set({ user: null, shop: null, currentDate: null }),
      setAuthStatus: (status) => set({ authStatus: status }),
      logout: () =>
        set({ user: null, shop: null, currentDate: null, authStatus: "unauthenticated" }),

      hasRole: (role) => get().user?.role === role,

      hasAnyRole: (roles) => {
        const role = get().user?.role;
        return role ? roles.includes(role) : false;
      },
    }),
    {
      name: "user-shop-storage",
      partialize: (state) =>
        ({
          user: state.user,
          shop: state.shop,
          currentDate: state.currentDate,
        }) as UserShopStore,
    },
  ),
);
