import React from "react";

interface PageHeaderProps {
  title: string;
}

export const PageHeader: React.FC<PageHeaderProps> = ({ title }) => {
  return (
    <div className="px-6 pt-12 pb-6">
      <h1 className="text-4xl font-bold mb-6">{title}</h1>
    </div>
  );
};
