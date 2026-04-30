import React, { useState, useRef, useEffect } from "react";

interface SelectOption {
  value: string;
  label: string;
}

interface FormSelectProps {
  label: string;
  name: string;
  value: string | null;
  onChange: (value: string) => void;
  options: SelectOption[];
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
    option?.label?.toLowerCase().includes(searchTerm.toLowerCase()),
  );

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
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
      <label htmlFor={name} className="mb-2 block text-sm font-medium text-slate-700">
        {label}
      </label>
      <div className="relative" ref={dropdownRef}>
        {/* Selected value display */}
        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          className="flex w-full items-center justify-between rounded-md border border-slate-300 bg-white px-4 py-3 text-left focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-100"
        >
          <span className={selectedOption ? "text-slate-950" : "text-slate-400"}>
            {selectedOption ? selectedOption.label : "Оберіть..."}
          </span>
          <svg
            className={`h-5 w-5 text-slate-500 transition-transform ${isOpen ? "rotate-180" : ""}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        {/* Dropdown */}
        {isOpen && (
          <div className="relative z-50 mt-2 w-full overflow-hidden rounded-md border border-slate-200 bg-white shadow-lg">
            {/* Search input */}
            <div className="border-b border-slate-100 p-3">
              <input
                type="text"
                placeholder="Пошук категорії..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full rounded-md bg-slate-50 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-100"
                onClick={(e) => e.stopPropagation()}
              />
            </div>

            {/* Options list */}
            <div className="max-h-40 overflow-y-auto">
              {filteredOptions.length > 0 ? (
                filteredOptions.map((option) => (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => handleSelect(option.value)}
                    className={`w-full px-4 py-3 text-left transition-colors hover:bg-slate-50 ${
                      value === option.value ? "bg-blue-50 text-blue-700" : "text-slate-700"
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
              <div className="border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => {
                    onAddCategory();
                    setIsOpen(false);
                    setSearchTerm("");
                  }}
                  className="flex w-full items-center gap-2 px-4 py-3 text-left font-medium text-blue-700 transition-colors hover:bg-blue-50"
                >
                  <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
        value={value ?? ""}
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
