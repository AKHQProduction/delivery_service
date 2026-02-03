import React from "react";

interface MenuCardProps {
  label: string;
  description: string;
  icon: string;
  onClick: () => void;
  disabled?: boolean;
}

export const MenuCard: React.FC<MenuCardProps> = ({
  label,
  description,
  icon,
  onClick,
  disabled = false,
}) => {
  return (
    <button
      type="button"
      onClick={disabled ? undefined : onClick}
      disabled={disabled}
      className={`group relative bg-white rounded-2xl shadow-sm transition-all duration-300 p-6 text-left border overflow-hidden ${
        disabled
          ? "opacity-60 cursor-not-allowed border-gray-200"
          : "hover:shadow-xl border-gray-100"
      }`}
    >
      {/* Gradient Background on Hover */}
      {!disabled && (
        <div className="absolute inset-0 bg-gradient-to-r from-indigo-50 to-purple-50 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
      )}

      {/* Content */}
      <div className="relative flex items-center gap-5">
        {/* Icon Container with Animation */}
        <div
          className={`w-16 h-16 rounded-2xl flex items-center justify-center shrink-0 shadow-lg transition-transform duration-300 ${
            disabled
              ? "bg-gray-300"
              : "bg-gradient-to-br from-indigo-500 to-purple-600 group-hover:scale-110 group-hover:rotate-3"
          }`}
        >
          <img
            src={icon}
            alt={label}
            className="w-8 h-8 object-contain brightness-0 invert"
          />
        </div>

        {/* Text Content */}
        <div className="flex-1 min-w-0">
          <h3
            className={`text-xl font-bold mb-1.5 transition-colors ${
              disabled
                ? "text-gray-500"
                : "text-gray-900 group-hover:text-indigo-600"
            }`}
          >
            {label}
          </h3>
          <p className="text-sm text-gray-600 leading-relaxed">
            {description}
          </p>
        </div>

        {/* Arrow Icon or Lock Icon */}
        <div className="shrink-0">
          {disabled ? (
            <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center">
              <svg
                className="w-5 h-5 text-gray-500"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                />
              </svg>
            </div>
          ) : (
            <div className="w-10 h-10 rounded-full bg-gray-100 group-hover:bg-indigo-100 flex items-center justify-center transition-all duration-300 group-hover:translate-x-1">
              <svg
                className="w-5 h-5 text-gray-400 group-hover:text-indigo-600 transition-colors"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2.5}
                  d="M9 5l7 7-7 7"
                />
              </svg>
            </div>
          )}
        </div>
      </div>

      {/* Bottom Accent Line */}
      {!disabled && (
        <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-indigo-500 to-purple-600 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left" />
      )}
    </button>
  );
};
