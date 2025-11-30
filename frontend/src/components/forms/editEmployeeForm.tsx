import React, { useState } from "react";
import { FormWrapper } from "../ui/formWrapper";
import { FormInput } from "../ui/formInput";
import { FormSelect } from "../ui/formSelect";

interface Employee {
  full_name: string;
  role: string;
  user_id: string;
}

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
    role: employee.role,
  });

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const updatedProduct = {
      user_id: employee.user_id,
      full_name: formData.full_name,
      role: formData.role,
    };

    onSave(updatedProduct);
    onClose();
  };

  const categoryOptions = [
    { value: "Менеджер", label: "Менеджер" },
    { value: "Кур'єр", label: "Кур'єр" },
  ];

  return (
    <FormWrapper
      onSubmit={handleSubmit}
      onClose={onClose}
      submitLabel="Зберегти зміни"
    >
      <FormInput
        label="Ім'я працівника"
        name="full_name"
        value={formData.full_name}
        onChange={handleChange}
        placeholder="Введіть ім'я..."
        required
      />
      <FormSelect
        label="Роль працівника"
        name="role"
        value={formData.role}
        onChange={handleChange}
        options={categoryOptions}
        required
      />
    </FormWrapper>
  );
};
