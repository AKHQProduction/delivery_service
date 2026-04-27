import React, { useEffect, useState } from "react";
import { FormWrapper } from "../../shared/FormWrapper";
import { FormInput } from "../../shared/FormInput";
import { FormSelect } from "../../shared/FormSelect";
import { AddressInputList } from "../../shared/AddressInputList";
import { PhoneInputList } from "../../shared/PhoneInputList";
import { type Client } from "../../../types/entities/Client";
import { useClientForm } from "../../../hooks/clients/useClientForm";
import { useDistrictsSettings } from "../../../hooks/settings/useDistrictsSettings";
import { useTimeSlotsSettings } from "../../../hooks/settings/useTimeSlotsSettings";
import { updateExistingClientById } from "../../../services/api/clientApi";
import { DuplicatePhoneToast } from "../../ui/PhoneDuplicateErrorPopup";

interface ExistingClient {
  id: string;
  full_name: string;
}

interface DuplicatePhone {
  phone_number: string;
  existing_clients: ExistingClient[];
}

interface EditClientFormProps {
  client: Client;
  onClose: () => void;
  onSave?: () => Promise<void> | void;
}

export const EditClientForm: React.FC<EditClientFormProps> = ({ client, onClose, onSave }) => {
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
  const { districts } = useDistrictsSettings();
  const { timeSlots } = useTimeSlotsSettings();
  const [balance, setBalance] = useState("");
  const [balanceError, setBalanceError] = useState<string | null>(null);
  const [phoneErrors, setPhoneErrors] = useState<Record<string, string>>({});
  const [duplicateError, setDuplicateError] = useState<{
    code: string;
    duplicates: DuplicatePhone[];
  } | null>(null);
  const [pendingClientData, setPendingClientData] = useState<typeof formData | null>(null);
  useEffect(() => {
    if (client) {
      initializeForm(client);
      setBalance(String(client.balance ?? 0));
      setBalanceError(null);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [client]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const timeSlotOptions = timeSlots.map((slot) => ({
    value: slot.time_slot_id,
    label: slot.label
      ? `${slot.label} (${slot.start_time} - ${slot.end_time})`
      : `${slot.start_time} - ${slot.end_time}`,
  }));

  const buildPayload = (clientData: typeof formData, nextBalance: number) => ({
    full_name: clientData.full_name,
    preferred_time_slot_id: clientData.preferred_time_slot_id || null,
    balance: nextBalance,
    phones: clientData.phones.filter((p) => p.number.trim() !== ""),
    addresses: clientData.addresses.filter((a) => a.street.trim() !== ""),
  });

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
    setBalanceError(null);

    const nextBalance = Number(balance.replace(",", "."));
    if (Number.isNaN(nextBalance)) {
      setBalanceError("Будь ласка, введіть коректне число.");
      return;
    }

    try {
      await updateExistingClientById(client.client_id, buildPayload(formData, nextBalance));
      await onSave?.();
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

    const nextBalance = Number(balance.replace(",", "."));
    if (Number.isNaN(nextBalance)) {
      setBalanceError("Будь ласка, введіть коректне число.");
      return;
    }

    try {
      await updateExistingClientById(
        client.client_id,
        buildPayload(pendingClientData, nextBalance),
        true,
      );
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
      <FormWrapper onSubmit={handleSubmit} onClose={onClose} submitLabel="Зберегти зміни">
        <FormInput
          label="Ім'я клієнта"
          name="full_name"
          value={formData.full_name}
          onChange={handleChange}
          placeholder="Введіть повне ім'я..."
          required
        />

        <FormInput
          label="Баланс"
          name="balance"
          type="text"
          value={balance}
          onChange={(e) => {
            setBalance(e.target.value);
            if (balanceError) {
              setBalanceError(null);
            }
          }}
          placeholder="Наприклад 1500 або -250"
          required
        />
        {balanceError && <p className="text-sm text-red-600">{balanceError}</p>}

        <FormSelect
          label="Бажаний час доставки"
          name="preferred_time_slot_id"
          value={formData.preferred_time_slot_id}
          onChange={handleChange}
          options={timeSlotOptions}
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
