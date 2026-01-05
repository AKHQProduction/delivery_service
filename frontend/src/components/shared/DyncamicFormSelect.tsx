import React, { useState, useRef, useEffect } from "react";

interface FormSelectProps {
  label: string;
  name: string;
  value: string;
  onChange: (value: any) => void;
  options: any[];
  required?: boolean;
  onAddCategory?: () => void;
}

export const DynamicFormSelect: React.FC<FormSelectProps> = ({
  label,
  name,
  value,
  onChange,
  options,
  required = false,
  onAddCategory,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const dropdownRef = useRef<HTMLDivElement>(null);

  const selectedOption = options.find((opt) => opt.value === value);

  const filteredOptions = options.filter((option) =>
    option?.label?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
        setSearchTerm("");
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSelect = (optionValue: string) => {
    onChange(optionValue);
    setIsOpen(false);
    setSearchTerm("");
  };

  return (
    <div>
      <label
        htmlFor={name}
        className="block text-sm font-medium text-gray-700 mb-2"
      >
        {label}
      </label>
      <div className="relative" ref={dropdownRef}>
        {/* Selected value display */}
        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-left flex items-center justify-between"
        >
          <span className={selectedOption ? "text-gray-900" : "text-gray-400"}>
            {selectedOption ? selectedOption.label : "Оберіть..."}
          </span>
          <svg
            className={`w-5 h-5 text-gray-400 transition-transform ${
              isOpen ? "rotate-180" : ""
            }`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 9l-7 7-7-7"
            />
          </svg>
        </button>

        {/* Dropdown */}
        {isOpen && (
          <div className="absolute z-50 w-full mt-2 bg-white border border-gray-200 rounded-xl shadow-lg overflow-hidden">
            {/* Search input */}
            <div className="p-3 border-b border-gray-100">
              <input
                type="text"
                placeholder="Пошук категорії..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-3 py-2 text-sm bg-gray-50 border-0 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                onClick={(e) => e.stopPropagation()}
              />
            </div>

            {/* Options list */}
            <div className="max-h-60 overflow-y-auto">
              {filteredOptions.length > 0 ? (
                filteredOptions.map((option) => (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => handleSelect(option.value)}
                    className={`w-full px-4 py-3 text-left hover:bg-gray-50 transition-colors ${
                      value === option.value
                        ? "bg-indigo-50 text-indigo-600"
                        : "text-gray-700"
                    }`}
                  >
                    {option.label}
                  </button>
                ))
              ) : (
                <div className="px-4 py-3 text-sm text-gray-500 text-center">
                  Категорії не знайдено
                </div>
              )}
            </div>

            {/* Add new category button */}
            {onAddCategory && (
              <div className="border-t border-gray-100">
                <button
                  type="button"
                  onClick={() => {
                    onAddCategory();
                    setIsOpen(false);
                    setSearchTerm("");
                  }}
                  className="w-full px-4 py-3 text-left text-indigo-600 hover:bg-indigo-50 transition-colors flex items-center gap-2 font-medium"
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
                      d="M12 4v16m8-8H4"
                    />
                  </svg>
                  Додати нову категорію
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Hidden select for form compatibility */}
      <select
        id={name}
        name={name}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        required={required}
        className="sr-only"
        tabIndex={-1}
      >
        <option value="">Оберіть...</option>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  );
};
