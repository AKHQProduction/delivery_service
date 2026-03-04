import React from "react";

interface SelectOption {
  value: string;
  label: string;
}

interface FormSelectProps {
  label: string;
  name: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLSelectElement>) => void;
  options: SelectOption[];
  required?: boolean;
}

export const FormSelect: React.FC<FormSelectProps> = ({
  label,
  name,
  value,
  onChange,
  options,
  required = false,
}) => {
  return (
    <div>
      <label htmlFor={name} className="block text-xs sm:text-sm font-medium text-gray-600 sm:text-gray-700 mb-1.5">
        {label}
      </label>
      <div className="relative">
        <select
          id={name}
          name={name}
          value={value}
          onChange={onChange}
          required={required}
          className="w-full h-12 px-3 sm:px-4 pr-10 bg-white border-2 border-indigo-200 rounded-lg sm:rounded-xl
                     focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent
                     text-gray-900 font-medium transition-all text-sm sm:text-base appearance-none"
        >
        {(!required || value === "") && <option value="">Оберіть...</option>}
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
        </select>
        <svg className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-900" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </div>
  );
};
