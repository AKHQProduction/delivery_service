import { useState, useEffect } from "react";
import {
  type Client,
  type Address,
  type Phone,
} from "../../types/entities/Client";

export const useClientForm = (initialData?: Partial<Client>) => {
  const [formData, setFormData] = useState({
    full_name: "",
    custom_id: "",
    phones: [{ number: "", is_primary: true, id: 0 }] as Phone[],
    addresses: [
      {
        street: "",
        house: "",
        apartment: "",
        entrance: "",
        floor: "",
        intercom: "",
        is_primary: true,
        comment: "",
      },
    ] as Address[],
  });

  useEffect(() => {
    if (initialData) {
      setFormData((prev) => ({ ...prev, ...initialData }));
    }
  }, [initialData]);

  const initializeForm = (client: Client) => {
    setFormData({
      full_name: client.full_name || "",
      custom_id: client.custom_id || "",
      phones:
        client.phones && client.phones.length > 0
          ? client.phones.map((phone) => ({
              id: phone.id || 0,
              number: phone.number || "",
              is_primary: phone.is_primary || false,
            }))
          : [{ number: "", is_primary: true }],
      addresses:
        client.addresses && client.addresses.length > 0
          ? client.addresses.map((address) => ({
              street: address.street || "",
              house: address.house || "",
              apartment: address.apartment || "",
              entrance: address.entrance || "",
              floor: address.floor || "",
              intercom: address.intercom || "",
              is_primary: address.is_primary || false,
              comment: address.comment || "",
            }))
          : [
              {
                street: "",
                house: "",
                apartment: "",
                entrance: "",
                floor: "",
                intercom: "",
                is_primary: true,
                comment: "",
              },
            ],
    });
  };

  const resetForm = () => {
    setFormData({
      full_name: "",
      custom_id: "",
      phones: [{ number: "", is_primary: true }],
      addresses: [
        {
          street: "",
          house: "",
          apartment: "",
          entrance: "",
          floor: "",
          intercom: "",
          is_primary: true,
          comment: "",
        },
      ],
    });
  };
  const handlePhoneChange = (index: number, value: string) => {
    setFormData((prev) => {
      const phones = [...prev.phones];
      phones[index] = { ...phones[index], number: value };
      return { ...prev, phones };
    });
  };

  const addPhone = () => {
    setFormData((prev) => ({
      ...prev,
      phones: [...prev.phones, { number: "", is_primary: false }],
    }));
  };

  const removePhone = (index: number) => {
    setFormData((prev) => {
      if (prev.phones.length > 1) {
        return {
          ...prev,
          phones: prev.phones.filter((_, i) => i !== index),
        };
      }
      return prev;
    });
  };

  const setPrimaryPhone = (index: number) => {
    setFormData((prev) => ({
      ...prev,
      phones: prev.phones.map((p, i) => ({
        ...p,
        is_primary: i === index,
      })),
    }));
  };

  const handleAddressChange = (
    index: number,
    field: keyof Address,
    value: string
  ) => {
    setFormData((prev) => {
      const addresses = [...prev.addresses];
      addresses[index] = { ...addresses[index], [field]: value };
      return { ...prev, addresses };
    });
  };

  const addAddress = () => {
    setFormData((prev) => ({
      ...prev,
      addresses: [
        ...prev.addresses,
        {
          street: "",
          house: "",
          apartment: "",
          entrance: "",
          floor: "",
          intercom: "",
          is_primary: false,
          comment: "",
        },
      ],
    }));
  };

  const removeAddress = (index: number) => {
    setFormData((prev) => {
      if (prev.addresses.length > 1) {
        return {
          ...prev,
          addresses: prev.addresses.filter((_, i) => i !== index),
        };
      }
      return prev;
    });
  };

  const setPrimaryAddress = (index: number) => {
    setFormData((prev) => ({
      ...prev,
      addresses: prev.addresses.map((a, i) => ({
        ...a,
        is_primary: i === index,
      })),
    }));
  };

  return {
    formData,
    setFormData,
    initializeForm,
    resetForm,
    handlePhoneChange,
    addPhone,
    removePhone,
    setPrimaryPhone,
    handleAddressChange,
    addAddress,
    removeAddress,
    setPrimaryAddress,
  };
};
