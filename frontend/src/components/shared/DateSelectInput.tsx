import React, { type FC } from "react";

interface DateSelectInputProps {
  label?: string;
  value: string;
  onChange: (date: string) => void;
  required?: boolean;
  minDate?: string;
  icon?: React.ReactNode;
}

export const DateSelectInput: FC<DateSelectInputProps> = ({
  label = "Оберіть дату",
  value,
  onChange,
  required = false,
  minDate = new Date().toISOString().split("T")[0],
  icon,
}) => {
  return (
    <div className="space-y-2">
      {label && (
        <label className="text-sm font-medium text-gray-700 flex items-center gap-2">
          {icon}
          {label}
          {required && <span className="text-red-500">*</span>}
        </label>
      )}

      <input
      title="Select date"
        type="date"
        value={value}
        min={minDate}
        onChange={(e) => onChange(e.target.value)}
        className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 font-medium"
      />
    </div>
  );
};
