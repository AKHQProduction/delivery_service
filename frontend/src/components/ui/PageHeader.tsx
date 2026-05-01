import React from "react";

interface PageHeaderProps {
  title: string;
}

export const PageHeader: React.FC<PageHeaderProps> = ({ title }) => {
  return (
    <div className="px-4 pt-6 pb-4 sm:px-6 md:px-8 md:pt-8 md:pb-5">
      <h1 className="text-2xl font-semibold leading-8 text-slate-950">{title}</h1>
    </div>
  );
};
