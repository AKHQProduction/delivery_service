import React from "react";

interface FormInputProps {
  label: string;
  name: string;
  type?: string;
  value: string | number;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  placeholder?: string;
  required?: boolean;
}

export const FormInput: React.FC<FormInputProps> = ({
  label,
  name,
  type = "text",
  value,
  onChange,
  placeholder,
  required = false,
}) => {
  return (
    <div>
      <label htmlFor={name} className="mb-2 block text-sm font-medium text-slate-700">
        {label}
      </label>
      <input
        id={name}
        name={name}
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        required={required}
        className="w-full rounded-md border border-slate-300 bg-white px-4 py-3 text-slate-950 placeholder:text-slate-400 focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-100"
      />
    </div>
  );
};
