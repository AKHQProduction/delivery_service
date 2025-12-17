import React from "react";
import { FormWrapper } from "../../shared/FormWrapper";
import { FormInput } from "../../shared/FormInput";
import { PhoneInputList } from "../../shared/PhoneInputList";
import { AddressInputList } from "../../shared/AddressInputList";
import { useClient } from "../../../hooks/clients/useClients";
import { useClientForm } from "../../../hooks/clients/useClientForm";

interface AddClientFormProps {
  onClose: () => void;
}

export const AddClientForm: React.FC<AddClientFormProps> = ({ onClose }) => {
  const {
    formData,
    setFormData,
    handlePhoneChange,
    addPhone,
    removePhone,
    setPrimaryPhone,
    handleAddressChange,
    addAddress,
    removeAddress,
    setPrimaryAddress,
  } = useClientForm();

  const { createClient } = useClient();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createClient(formData);
    onClose();
    window.location.reload(); //TEMPORARY SOLUTION
  };

  return (
    <FormWrapper
      onSubmit={handleSubmit}
      onClose={onClose}
      submitLabel="Додати клієнта"
    >
      <FormInput
        label="ID клієнта"
        name="custom_id"
        value={formData.custom_id || ""}
        onChange={handleChange}
        placeholder="Наприклад: NEW-ID-123"
      />
      <FormInput
        label="Ім'я клієнта"
        name="full_name"
        value={formData.full_name}
        onChange={handleChange}
        placeholder="Введіть повне ім'я..."
        required
      />

      <PhoneInputList
        phones={formData.phones}
        onPhoneChange={handlePhoneChange}
        onSetPrimary={setPrimaryPhone}
        onRemove={removePhone}
        onAdd={addPhone}
      />

      <AddressInputList
        addresses={formData.addresses}
        onAddressChange={handleAddressChange}
        onSetPrimary={setPrimaryAddress}
        onRemove={removeAddress}
        onAdd={addAddress}
      />
    </FormWrapper>
  );
};
