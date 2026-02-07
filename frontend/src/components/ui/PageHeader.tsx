import React from "react";

interface PageHeaderProps {
  title: string;
}

export const PageHeader: React.FC<PageHeaderProps> = ({ title }) => {
  return (
    <div className="px-6 pt-12 pb-6 lg:px-8 lg:pt-8 lg:pb-4">
      <h1 className="text-4xl font-bold mb-6 lg:text-3xl lg:mb-2">{title}</h1>
    </div>
  );
};
