import React, { useState } from "react";
import { FormWrapper } from "../ui/formWrapper";
import { FormInput } from "../ui/formInput";
import { DynamicInputList } from "../ui/dynamicInputList";

interface AddClientFormProps {
  onClose: () => void;
}

export const AddClientForm: React.FC<AddClientFormProps> = ({ onClose }) => {
  const [formData, setFormData] = useState({
    client_id: "",
    name: "",
    phones: [""],
    addresses: [""],
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const cleanedData = {
      ...formData,
      phones: formData.phones.filter((p) => p.trim() !== ""),
      addresses: formData.addresses.filter((a) => a.trim() !== ""),
    };
    console.log("Client submitted:", cleanedData);
    onClose();
  };

  return (
    <FormWrapper
      onSubmit={handleSubmit}
      onClose={onClose}
      submitLabel="Додати клієнта"
    >
      <FormInput
        label="ID клієнта"
        name="client_id"
        value={formData.client_id}
        onChange={handleChange}
        placeholder="Наприклад: БИДЛ001"
        required
      />
      <FormInput
        label="Ім'я клієнта"
        name="name"
        value={formData.name}
        onChange={handleChange}
        placeholder="Введіть ім'я..."
        required
      />

      <DynamicInputList
        label="Телефони"
        values={formData.phones}
        onChange={(phones) => setFormData({ ...formData, phones })}
        placeholder="+380..."
        type="tel"
        required
        addButtonLabel="+ Додати телефон"
      />

      <DynamicInputList
        label="Адреси"
        values={formData.addresses}
        onChange={(addresses) => setFormData({ ...formData, addresses })}
        placeholder="Введіть адресу..."
        addButtonLabel="+ Додати адресу"
      />
    </FormWrapper>
  );
};
