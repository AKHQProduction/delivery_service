import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { User, Shop } from "../types/entities/user";
import { UserRole } from "../constants/roles";

interface UserShopStore {
  user: User | null;
  shop: Shop | null;

  setUser: (u: User | null) => void;
  setShop: (s: Shop | null) => void;
  setUserAndShop: (user: User | null, shop: Shop | null) => void;
  clear: () => void;

  hasRole: (role: UserRole) => boolean;
  hasAnyRole: (roles: UserRole[]) => boolean;
}

export const useUserShopStore = create(
  persist<UserShopStore>(
    (set, get) => ({
      user: null,
      shop: null,

      setUser: (u) => set({ user: u }),
      setShop: (s) => set({ shop: s }),
      setUserAndShop: (user, shop) => set({ user, shop }),
      clear: () => set({ user: null, shop: null }),

      hasRole: (role) => get().user?.role === role,

      hasAnyRole: (roles) => {
        const role = get().user?.role;
        return role ? roles.includes(role) : false;
      },
    }),
    {
      name: "user-shop-storage",
    },
  ),
);
