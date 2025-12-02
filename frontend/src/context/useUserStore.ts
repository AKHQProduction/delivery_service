import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { User } from "../types/entities/user";
import { UserRole } from "../constants/roles";

interface UserStore {
  user: User | null;

  setUser: (u: User | null) => void;
  removeUserRole: () => void;

  hasRole: (role: UserRole) => boolean;
  hasAnyRole: (roles: UserRole[]) => boolean;
}

export const useUserStore = create(
  persist<UserStore>(
    (set, get) => ({
      user: null,

      setUser: (u) => set({ user: u }),
      removeUserRole: () => set({ user: null }),

      hasRole: (role) => get().user?.role === role,

      hasAnyRole: (roles) => {
        const role = get().user?.role;
        return role ? roles.includes(role) : false;
      },
    }),
    {
      name: "app-user-storage",
    }
  )
);
