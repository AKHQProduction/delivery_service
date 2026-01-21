import React, { useState } from "react";

type FilterProps = {
  title?: string;
  children: React.ReactNode;
  onApply?: () => void;
  buttonTitle?: string;
  width?: string;
};

export const SearchFiltersPopup = ({
  title = "Фільтр",
  children,
  onApply,
  buttonTitle = "Фільтр",
  width = "w-72",
}: FilterProps) => {
  const [isOpen, setIsOpen] = useState(false);

  const handleApply = () => {
    onApply?.();
    setIsOpen(false);
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`p-2 rounded-lg transition-colors ${
          isOpen ? "text-indigo-600" : "text-gray-500 hover:text-indigo-500"
        }`}
        title={buttonTitle}
      >
        <svg
          className="w-6 h-6"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"
          />
        </svg>
      </button>

      {isOpen && (
        <div
          className={`absolute right-0 top-full mt-2 ${width} bg-white rounded-lg shadow-lg border border-gray-200 p-4 z-10`}
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-gray-900">{title}</h3>
            <button
              type="button"
              title="filterButton"
              onClick={() => setIsOpen(false)}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>

          <div className="space-y-3">{children}</div>

          <div className="mt-4 flex gap-2">
            <button
              onClick={handleApply}
              className="flex-1 px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition-colors"
            >
              Пошук
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
