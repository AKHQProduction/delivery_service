import React from "react";

interface EmptyStateProps {
  title: string;
  description?: string;
  icon?: React.ReactNode;
}

export const EmptyState: React.FC<EmptyStateProps> = ({ title, description, icon }) => {
  return (
    <div className="flex min-h-80 flex-col items-center justify-center rounded-lg border border-slate-200 bg-white px-6 py-12 text-center">
      <div className="mb-5 flex h-14 w-14 items-center justify-center rounded-full bg-slate-100 text-slate-400">
        {icon || (
          <svg className="h-7 w-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 6h16M4 12h16M4 18h16"
            />
          </svg>
        )}
      </div>
      <p className="text-lg font-semibold text-slate-950">{title}</p>
      {description && (
        <p className="mt-2 max-w-sm text-sm leading-5 text-slate-500">{description}</p>
      )}
    </div>
  );
};
