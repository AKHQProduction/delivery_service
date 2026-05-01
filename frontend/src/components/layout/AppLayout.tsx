import React, { useMemo, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { SidebarNav } from "./SidebarNav";
import { useUserShopStore } from "../../context/useUserShopStore";
import { getShellRoutesForRole } from "../../config/roles.config";
import { MenuIcon, MobileDrawer } from "./MobileDrawer";

interface AppLayoutProps {
  children: React.ReactNode;
}

export const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  const user = useUserShopStore((s) => s.user);
  const navigate = useNavigate();
  const location = useLocation();
  const isOnboardingRoute = location.pathname === "/login" || location.pathname === "/create-shop";
  const showSidebar = !!user && !isOnboardingRoute;
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const menuButtonRef = useRef<HTMLButtonElement | null>(null);
  const drawerRoutes = useMemo(() => (user ? getShellRoutesForRole(user.role) : []), [user]);

  const closeDrawer = () => {
    menuButtonRef.current?.focus();
    setIsDrawerOpen(false);
  };

  return (
    <>
      <SidebarNav />
      {showSidebar && (
        <div className="fixed inset-x-0 top-0 z-40 flex h-14 items-center border-b border-slate-200 bg-white px-4 md:hidden">
          <button
            type="button"
            ref={menuButtonRef}
            onClick={() => setIsDrawerOpen(true)}
            className="inline-flex h-9 w-9 items-center justify-center rounded-md text-slate-700 hover:bg-slate-100"
            aria-label="Відкрити меню"
          >
            <MenuIcon className="h-5 w-5" />
          </button>
          <span className="ml-3 text-sm font-semibold text-slate-950">Water Delivery</span>
        </div>
      )}
      <div
        className={
          showSidebar
            ? "min-h-screen bg-slate-50 pt-14 md:pl-[17rem] md:pt-0"
            : "min-h-screen bg-slate-50"
        }
      >
        <div
          className={
            showSidebar ? "min-h-screen pb-24 md:mx-auto md:max-w-[1440px] md:pb-0" : "min-h-screen"
          }
        >
          {children}
        </div>
      </div>
      {showSidebar && (
        <MobileDrawer
          isOpen={isDrawerOpen}
          routes={drawerRoutes}
          userName={user?.full_name || ""}
          userRole={user?.role || ""}
          activePath={location.pathname}
          onClose={closeDrawer}
          onNavigate={(path) => {
            closeDrawer();
            navigate(path);
          }}
        />
      )}
    </>
  );
};
