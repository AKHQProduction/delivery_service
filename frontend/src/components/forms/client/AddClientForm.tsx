import React, { useState } from "react";
import { FormWrapper } from "../../shared/FormWrapper";
import { FormInput } from "../../shared/FormInput";
import { PhoneInputList } from "../../shared/PhoneInputList";
import { AddressInputList } from "../../shared/AddressInputList";
import { useClient } from "../../../hooks/clients/useClients";
import { useClientForm } from "../../../hooks/clients/useClientForm";
import { useDistrictsSettings } from "../../../hooks/settings/useDistrictsSettings";
import { type Client } from "../../../types/entities/Client";
import { DuplicatePhoneToast } from "../../ui/PhoneDuplicateErrorPopup";

interface ExistingClient {
  id: string;
  full_name: string;
}

interface DuplicatePhone {
  phone_number: string;
  existing_clients: ExistingClient[];
}

interface AddClientFormProps {
  onClose: () => void;
  onSuccess?: (client?: Client) => void;
}

export const AddClientForm: React.FC<AddClientFormProps> = ({ onClose, onSuccess }) => {
  const {
    formData,
    setFormData,
    handlePhoneChange: originalHandlePhoneChange,
    addPhone,
    removePhone,
    setPrimaryPhone,
    handleAddressChange,
    setAddressCoordinates,
    addAddress,
    removeAddress,
    setPrimaryAddress,
  } = useClientForm();

  const { createClient } = useClient();
  const { districts } = useDistrictsSettings();
  const [phoneErrors, setPhoneErrors] = useState<Record<string, string>>({});
  const [duplicateError, setDuplicateError] = useState<{
    code: string;
    duplicates: DuplicatePhone[];
  } | null>(null);
  const [pendingClientData, setPendingClientData] = useState<typeof formData | null>(null);

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setPhoneErrors({});

    try {
      const response = await createClient(formData, false);

      const clientId =
        typeof response === "string" ? response : (response?.client_id ?? response?.id);
      const fullClient: Client = {
        client_id: clientId,
        full_name: formData.full_name,
        phones: formData.phones.filter((p) => p.number.trim() !== ""),
        addresses: formData.addresses.filter((a) => a.street.trim() !== ""),
      };
      onSuccess?.(fullClient);
      onClose();
    } catch (err: unknown) {
      if (
        err &&
        typeof err === "object" &&
        "response" in err &&
        err.response &&
        typeof err.response === "object" &&
        "status" in err.response &&
        err.response.status === 409 &&
        "data" in err.response &&
        err.response.data &&
        typeof err.response.data === "object" &&
        "code" in err.response.data &&
        err.response.data.code === "duplicate_phones" &&
        "duplicates" in err.response.data &&
        Array.isArray(err.response.data.duplicates)
      ) {
        const errorData = err.response.data as { code: string; duplicates: DuplicatePhone[] };
        console.log("Duplicate phone detected:", errorData);
        setDuplicateError(errorData);
        setPendingClientData(formData);
      }
    }
  };

  const handleConfirmDuplicate = async () => {
    if (!pendingClientData) return;

    try {
      const response = await createClient(pendingClientData, true);

      const clientId =
        typeof response === "string" ? response : (response?.client_id ?? response?.id);
      const fullClient: Client = {
        client_id: clientId,
        full_name: pendingClientData.full_name,
        phones: pendingClientData.phones.filter((p) => p.number.trim() !== ""),
        addresses: pendingClientData.addresses.filter((a) => a.street.trim() !== ""),
      };

      setDuplicateError(null);
      setPendingClientData(null);
      onSuccess?.(fullClient);
      onClose();
    } catch (err) {
      console.error("Error confirming duplicate:", err);
      setDuplicateError(null);
      setPendingClientData(null);
    }
  };

  const handleCancelDuplicate = () => {
    setDuplicateError(null);
    setPendingClientData(null);
  };

  return (
    <>
      <FormWrapper onSubmit={handleSubmit} onClose={onClose} submitLabel="Додати клієнта">
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
          onCoordinatesChange={setAddressCoordinates}
          onSetPrimary={setPrimaryAddress}
          onRemove={removeAddress}
          onAdd={addAddress}
          districts={districts}
        />
      </FormWrapper>

      {duplicateError && duplicateError.duplicates && (
        <DuplicatePhoneToast
          duplicates={duplicateError.duplicates}
          onConfirm={handleConfirmDuplicate}
          onCancel={handleCancelDuplicate}
        />
      )}
    </>
  );
};
