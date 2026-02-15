import React from "react";
import { SidebarNav } from "./SidebarNav";
import { useUserShopStore } from "../../context/useUserShopStore";

interface AppLayoutProps {
  children: React.ReactNode;
}

export const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  const user = useUserShopStore((s) => s.user);

  return (
    <>
      <SidebarNav />
      <div className={user ? "lg:pl-64" : ""}>
        <div className={user ? "lg:max-w-5xl lg:mx-auto" : ""}>{children}</div>
      </div>
    </>
  );
};
