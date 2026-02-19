import React from "react";

interface PageHeaderProps {
  title: string;
}

export const PageHeader: React.FC<PageHeaderProps> = ({ title }) => {
  return (
    <div className="px-6 pt-12 pb-6 md:px-8 md:pt-8 md:pb-4">
      <h1 className="text-4xl font-bold mb-6 md:text-3xl md:mb-2">{title}</h1>
    </div>
  );
};
