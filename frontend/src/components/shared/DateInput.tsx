import React from "react";

interface DateInputProps {
  label?: string;
  value: string;
  onChange: (value: string) => void;
  title?: string;
  error?: boolean;
  required?: boolean;
  className?: string;
  variant?: "default" | "amber";
  minDate?: string;
  icon?: React.ReactNode;
}

export const DateInput: React.FC<DateInputProps> = ({
  label,
  value,
  onChange,
  title,
  error = false,
  required = false,
  className = "",
  variant = "default",
  minDate,
  icon,
}) => {
  const getBorderColor = () => {
    if (error) return "border-red-500";
    if (variant === "amber") return "border-amber-300";
    return "border-indigo-200";
  };

  const getFocusRingColor = () => {
    if (error) return "focus:ring-red-400";
    if (variant === "amber") return "focus:ring-amber-400";
    return "focus:ring-indigo-500";
  };

  return (
    <div className={className}>
      {label && (
        <label className="flex items-center gap-2 text-xs sm:text-sm font-medium text-gray-600 sm:text-gray-700 mb-1.5">
          {icon}
          {label}
          {required && <span className="text-red-500">*</span>}
        </label>
      )}
      <input
        title={title || label}
        type="date"
        value={value}
        min={minDate}
        onChange={(e) => onChange(e.target.value)}
        required={required}
        className={`w-full px-3 py-3 sm:px-4 sm:py-3.5 border-2 rounded-lg sm:rounded-xl bg-white
                   focus:outline-none focus:ring-2 focus:border-transparent
                   text-gray-900 font-medium transition-all text-sm sm:text-base
                   ${getBorderColor()} ${getFocusRingColor()}`}
        style={{ WebkitAppearance: "none", MozAppearance: "textfield" }}
      />
    </div>
  );
};
