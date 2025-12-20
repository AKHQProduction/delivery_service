import React, { useState } from "react";
import { FormWrapper } from "../../shared/FormWrapper";
import { FormInput } from "../../shared/FormInput";
import { PhoneInputList } from "../../shared/PhoneInputList";
import { AddressInputList } from "../../shared/AddressInputList";
import { useClient } from "../../../hooks/clients/useClients";
import { useClientForm } from "../../../hooks/clients/useClientForm";

interface AddClientFormProps {
  onClose: () => void;
  onSuccess?: () => void;
}

export const AddClientForm: React.FC<AddClientFormProps> = ({
  onClose,
  onSuccess,
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
  } = useClientForm();

  const { createClient } = useClient();
  const [phoneErrors, setPhoneErrors] = useState<Record<string, string>>({});

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
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
      await createClient(formData);
      onSuccess?.();
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
