import React from "react";

interface WelcomeSectionProps {
  title: string;
  subtitle: string;
}

export const WelcomeSection: React.FC<WelcomeSectionProps> = ({ title, subtitle }) => {
  return (
    <div className="mb-8">
      <h2 className="text-2xl font-bold text-gray-800 mb-2">{title}</h2>
      <p className="text-gray-600">{subtitle}</p>
    </div>
  );
};
