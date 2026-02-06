import React, { useEffect, useState } from "react";
import { FormWrapper } from "../../shared/FormWrapper";
import { FormInput } from "../../shared/FormInput";
import { AddressInputList } from "../../shared/AddressInputList";
import { PhoneInputList } from "../../shared/PhoneInputList";
import { type Client } from "../../../types/entities/Client";
import { useClient } from "../../../hooks/clients/useClients";
import { useClientForm } from "../../../hooks/clients/useClientForm";
import { useDistrictsSettings } from "../../../hooks/settings/useDistrictsSettings";
import { DuplicatePhoneToast } from "../../ui/PhoneDuplicateErrorPopup";
interface EditClientFormProps {
  client: Client;
  onClose: () => void;
  onSave?: () => Promise<void> | void;
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
    setAddressCoordinates,
    addAddress,
    removeAddress,
    setPrimaryAddress,
    initializeForm,
  } = useClientForm();
  const { updateClient } = useClient();
  const { districts } = useDistrictsSettings();
  const [phoneErrors, setPhoneErrors] = useState<Record<string, string>>({});
  const [duplicateError, setDuplicateError] = useState<any>(null);
  const [pendingClientData, setPendingClientData] = useState<any>(null);
  useEffect(() => {
    if (client) {
      initializeForm(client);
    }
  }, [client]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>,
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setPhoneErrors({});

    try {
      await updateClient(client.client_id, formData);
      await onSave?.();
    } catch (err: any) {
      if (
        err?.response?.status === 409 &&
        err?.response?.data?.code === "duplicate_phones"
      ) {
        console.log("Duplicate phone detected:", err.response.data);
        setDuplicateError(err.response.data);
        setPendingClientData(formData);
      }
    }
  };
  const handleConfirmDuplicate = async () => {
    if (!pendingClientData) return;

    try {
      await updateClient(client.client_id, formData, true);
      await onSave?.();

      setDuplicateError(null);
      setPendingClientData(null);

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