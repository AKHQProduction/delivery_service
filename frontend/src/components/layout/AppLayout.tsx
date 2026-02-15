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
      <div className={showSidebar ? "md:pl-64" : ""}>
        <div className={showSidebar ? "md:max-w-5xl md:mx-auto" : ""}>{children}</div>
      </div>
    </>
  );
};
