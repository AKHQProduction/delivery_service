import React, { useState } from "react";
import { FormWrapper } from "../../shared/FormWrapper";
import { FormInput } from "../../shared/FormInput";
import { FormSelect } from "../../shared/FormSelect";
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
      />
      <FormSelect
        label="Роль працівника"
        name="role"
        value={formData.role}
        onChange={handleChange}
        options={categoryOptions}
      />
    </FormWrapper>
  );
};
