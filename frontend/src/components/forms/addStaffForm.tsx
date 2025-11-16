import React, { useState } from "react";
import { FormWrapper } from "../ui/formWrapper";
import { FormInput } from "../ui/formInput";
import { FormSelect } from "../ui/formSelect";

interface AddStaffFormProps {
  onClose: () => void;
}

export const AddStaffForm: React.FC<AddStaffFormProps> = ({ onClose }) => {
  const [formData, setFormData] = useState({
    name: "",
    phone: "",
    role: "",
    email: "",
  });

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Staff submitted:", formData);
    onClose();
  };

  const roleOptions = [
    { value: "driver", label: "Водій" },
    { value: "manager", label: "Менеджер" },
    { value: "admin", label: "Адміністратор" },
  ];

  return (
    <FormWrapper
      onSubmit={handleSubmit}
      onClose={onClose}
      submitLabel="Додати співробітника"
    >
      <FormInput
        label="Ім'я співробітника"
        name="name"
        value={formData.name}
        onChange={handleChange}
        placeholder="Введіть ім'я..."
        required
      />
      <FormInput
        label="Телефон"
        name="phone"
        type="tel"
        value={formData.phone}
        onChange={handleChange}
        placeholder="+380..."
        required
      />
      <FormInput
        label="Email"
        name="email"
        type="email"
        value={formData.email}
        onChange={handleChange}
        placeholder="email@example.com"
        required
      />
      <FormSelect
        label="Посада"
        name="role"
        value={formData.role}
        onChange={handleChange}
        options={roleOptions}
        required
      />
    </FormWrapper>
  );
};
