import React, { useState } from "react";
import { FormWrapper } from "./formWrapper";
import { FormInput } from "./formInput";

interface AddClientFormProps {
  onClose: () => void;
}

export const AddClientForm: React.FC<AddClientFormProps> = ({ onClose }) => {
  const [formData, setFormData] = useState({
    name: "",
    phone: "",
    email: "",
    address: "",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Client submitted:", formData);
    onClose();
  };

  return (
    <FormWrapper onSubmit={handleSubmit} onClose={onClose} submitLabel="Додати клієнта">
      <FormInput
        label="Ім'я клієнта"
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
      />
      <FormInput
        label="Адреса"
        name="address"
        value={formData.address}
        onChange={handleChange}
        placeholder="Введіть адресу..."
      />
    </FormWrapper>
  );
};