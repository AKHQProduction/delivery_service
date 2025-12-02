import React, { useState } from "react";
import { FormWrapper } from "../shared/FormWrapper";
import { FormInput } from "../shared/FormInput";
import { FormSelect } from "../shared/FormSelect";
import { useEmployees } from "../../../hooks/useEmployees";

export const InviteUserForm: React.FC<{
  onClose: () => void;
  onInviteCreated: (link: string) => void;
}> = ({ onClose, onInviteCreated }) => {
  const [formData, setFormData] = useState({
    name: "",
    role: "",
  });

  const { createInviteLink } = useEmployees();

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const link = await createInviteLink(formData.role, formData.name);

    onInviteCreated(link); // передаем наверх
    onClose(); // закрываем модалку
  };

  const roleOptions = [
    { value: "MANAGER", label: "Менеджер" },
    { value: "COURIER", label: "Кур'єр" },
  ];

  return (
    <FormWrapper
      onSubmit={handleSubmit}
      onClose={onClose}
      submitLabel="Запросити співробітника"
    >
      <FormInput
        label="Ім'я співробітника"
        name="name"
        value={formData.name}
        onChange={handleChange}
        placeholder="Введіть ім'я..."
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
