import React, { useState } from "react";
import { FormWrapper } from "../ui/formWrapper";
import { FormInput } from "../ui/formInput";
import { DynamicInputList } from "../ui/dynamicInputList";
import { type Client } from "../../types/entities/Client";

interface EditClientFormProps {
  client: Client;
  onClose: () => void;
  onSave: (updatedEmployee: Client) => void;
}

export const EditClientForm: React.FC<EditClientFormProps> = ({
  client,
  onClose,
  onSave,
}) => {
  const [formData, setFormData] = useState({
    full_name: client.full_name,
    number: client.number.length > 0 ? client.number : [""],
    adress: client.adress.length > 0 ? client.adress : [""],
  });

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const updatedClient = {
      client_id: client.client_id,
      full_name: formData.full_name,
      number: formData.number.filter((p) => p.trim() !== ""),
      adress: formData.adress.filter((a) => a.trim() !== ""),
    };

    onSave(updatedClient);
    onClose();
  };

  return (
    <FormWrapper
      onSubmit={handleSubmit}
      onClose={onClose}
      submitLabel="Зберегти зміни"
    >
      <FormInput
        label="Ім'я клієнта"
        name="full_name"
        value={formData.full_name}
        onChange={handleChange}
        placeholder="Введіть ім'я..."
        required
      />

      <DynamicInputList
        label="Телефони"
        values={formData.number}
        onChange={(number) => setFormData({ ...formData, number })}
        placeholder="+380..."
        type="tel"
        required
        addButtonLabel="+ Додати телефон"
      />

      <DynamicInputList
        label="Адреси"
        values={formData.adress}
        onChange={(adress) => setFormData({ ...formData, adress })}
        placeholder="Введіть адресу..."
        addButtonLabel="+ Додати адресу"
      />
    </FormWrapper>
  );
};
