import React, { useEffect } from "react";
import { FormWrapper } from "../../shared/FormWrapper";
import { FormInput } from "../../shared/FormInput";
import { AddressInputList } from "../../shared/AddressInputList";
import { PhoneInputList } from "../../shared/PhoneInputList";
import { type Client } from "../../../types/entities/Client";
import { useClient } from "../../../hooks/clients/useClients";
import { useClientForm } from "../../../hooks/clients/useClientForm";
interface EditClientFormProps {
  client: Client;
  onClose: () => void;
  onSave: (updatedClient: Client) => void;
}

export const EditClientForm: React.FC<EditClientFormProps> = ({
  client,
  onClose,
}) => {
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
    initializeForm,
  } = useClientForm();
  const { updateClient } = useClient();

  useEffect(() => {
    if (client) {
      initializeForm(client);
    }
  }, [client]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    updateClient(client.client_id, formData);
    onClose();
    window.location.reload(); //TEMPORARY SOLUTION
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
