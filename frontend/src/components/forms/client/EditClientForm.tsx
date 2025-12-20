import React, { useEffect, useState } from "react";
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
  onSave?: () => void;
}

export const EditClientForm: React.FC<EditClientFormProps> = ({
  client,
  onClose,
  onSave,
}) => {
  const {
    formData,
    setFormData,
    handlePhoneChange: originalHandlePhoneChange,
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
  const [phoneErrors, setPhoneErrors] = useState<Record<string, string>>({});

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

  const handlePhoneChange = (index: number, value: string) => {
    const oldNumber = formData.phones[index]?.number;
    if (oldNumber && phoneErrors[oldNumber]) {
      setPhoneErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[oldNumber];
        return newErrors;
      });
    }
    originalHandlePhoneChange(index, value);
  };

  const extractPhoneFromError = (errorMessage: string): string | null => {
    const match = errorMessage.match(/Phone number (\+?\d+)/);
    return match ? match[1] : null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setPhoneErrors({});

    try {
      await updateClient(client.client_id, formData);
      onSave?.();
      onClose();
    } catch (err: any) {
      const errorMessage = err?.message || "";
      const phoneNumber = extractPhoneFromError(errorMessage);

      if (phoneNumber) {
        setPhoneErrors({
          [phoneNumber]: "Цей номер вже використовується іншим клієнтом",
        });
      }
    }
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
      <FormInput
        label="Тег клієнта"
        name="custom_id"
        value={formData.custom_id || ""}
        onChange={handleChange}
        placeholder="Наприклад: VIP-001"
      />

      <PhoneInputList
        phones={formData.phones}
        onPhoneChange={handlePhoneChange}
        onSetPrimary={setPrimaryPhone}
        onRemove={removePhone}
        onAdd={addPhone}
        errors={phoneErrors}
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
