import React from "react";
import { SidebarNav } from "./SidebarNav";

interface AppLayoutProps {
  children: React.ReactNode;
}

export const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  return (
    <>
      <SidebarNav />
      <div className="lg:pl-64">
        <div className="lg:max-w-5xl lg:mx-auto">{children}</div>
      </div>
    </>
  );
};
