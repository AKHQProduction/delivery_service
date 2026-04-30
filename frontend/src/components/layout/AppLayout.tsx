import React from "react";
import { SidebarNav } from "./SidebarNav";
import { useUserShopStore } from "../../context/useUserShopStore";

interface AppLayoutProps {
  children: React.ReactNode;
}

export const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  const user = useUserShopStore((s) => s.user);
  const showSidebar = !!user;

  return (
    <>
      <SidebarNav />
      <div
        className={
          showSidebar ? "min-h-screen bg-slate-50 md:pl-[17rem]" : "min-h-screen bg-slate-50"
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
    </>
  );
};
