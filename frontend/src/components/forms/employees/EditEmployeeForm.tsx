import React, { useState } from "react";
import { FormWrapper } from "../../shared/FormWrapper";
import { FormInput } from "../../shared/FormInput";
import { type Employee } from "../../../types/entities/Employee";
import { roleMap } from "../../../utils/dataMap";

interface EditEmployeeFormProps {
  employee: Employee;
  onClose: () => void;
  onSave: (updatedEmployee: Employee) => void;
}

export const EditEmployeeForm: React.FC<EditEmployeeFormProps> = ({
  employee,
  onClose,
  onSave,
}) => {
  const [formData, setFormData] = useState({
    full_name: employee.full_name,
    role: roleMap[employee.role] || employee.role,
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!employee?.user_id) {
      console.error("Cannot save: employee or user_id is missing");
      return;
    }

    const updatedEmployee: Employee = {
      user_id: employee.user_id,
      full_name: formData.full_name,
      role: formData.role,
    };

    onSave(updatedEmployee);
  };

  const categoryOptions = [
    { value: "Менеджер", label: "Менеджер" },
    { value: "Кур'єр", label: "Кур'єр" },
  ];

  return (
    <FormWrapper onSubmit={handleSubmit} onClose={onClose} submitLabel="Зберегти зміни">
      <FormInput
        label="Ім'я працівника"
        name="full_name"
        value={formData.full_name}
        onChange={handleChange}
        placeholder="Введіть ім'я..."
      />
      <div>
        <label htmlFor="role" className="mb-2 block text-sm font-medium text-slate-700">
          Роль працівника
        </label>
        <div className="relative">
          <select
            id="role"
            name="role"
            value={formData.role}
            onChange={handleChange}
            className="h-12 w-full appearance-none rounded-md border border-slate-300 bg-white px-4 pr-10 text-slate-950 focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-100"
          >
            {categoryOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          <svg
            className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="m19 9-7 7-7-7" />
          </svg>
        </div>
      </div>
    </FormWrapper>
  );
};
