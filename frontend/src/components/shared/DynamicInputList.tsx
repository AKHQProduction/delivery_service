import React from "react";

interface DynamicInputListProps {
  label: string;
  values: string[];
  onChange: (values: string[]) => void;
  placeholder?: string;
  required?: boolean;
  type?: "text" | "tel" | "email";
  addButtonLabel?: string;
}

export const DynamicInputList: React.FC<DynamicInputListProps> = ({
  label,
  values,
  onChange,
  placeholder = "",
  required = false,
  type = "text",
  addButtonLabel = "+ Додати",
}) => {
  const handleValueChange = (index: number, value: string) => {
    const newValues = [...values];
    newValues[index] = value;
    onChange(newValues);
  };

  const addValue = () => {
    onChange([...values, ""]);
  };

  const removeValue = (index: number) => {
    if (values.length > 1) {
      const newValues = values.filter((_, i) => i !== index);
      onChange(newValues);
    }
  };

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">
        {label} {required && <span className="text-red-500">*</span>}
      </label>
      {values.map((value, index) => (
        <div key={index} className="flex gap-2">
          <input
            type={type}
            value={value}
            onChange={(e) => handleValueChange(index, e.target.value)}
            placeholder={placeholder}
            required={required && index === 0}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 transition-shadow"
          />
          {values.length > 1 && (
            <button
              type="button"
              onClick={() => removeValue(index)}
              className="px-3 py-2 text-red-600 hover:bg-red-50 rounded-md transition-colors"
              aria-label={`Видалити ${label.toLowerCase()}`}
            >
              ✕
            </button>
          )}
        </div>
      ))}
      <button
        type="button"
        onClick={addValue}
        className="text-sm text-blue-600 hover:text-blue-700 font-medium transition-colors"
      >
        {addButtonLabel}
      </button>
    </div>
  );
};
