import React, { useState } from "react";
import { FormWrapper } from "../shared/FormWrapper";
import { FormInput } from "../shared/FormInput";
import { FormSelect } from "../shared/FormSelect";

interface AddOrderFormProps {
  onClose: () => void;
}

export const AddOrderForm: React.FC<AddOrderFormProps> = ({ onClose }) => {
  const [formData, setFormData] = useState({
    clientName: "",
    product: "",
    quantity: "",
    deliveryDate: "",
    address: "",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Order submitted:", formData);
    onClose();
  };
  //Temporary hardcoded values
  const productOptions = [
    { value: "water_karpatska", label: 'Вода "Карпатська"' },
    { value: "water_morshynska", label: 'Вода "Моршинська"' },
    { value: "water_bonaqua", label: 'Вода "BonAqua"' },
    { value: "pump", label: "Помпа для води" },
  ];

  return (
    <FormWrapper onSubmit={handleSubmit} onClose={onClose} submitLabel="Створити замовлення">
      <FormInput
        label="Клієнт"
        name="clientName"
        value={formData.clientName}
        onChange={handleChange}
        placeholder="Оберіть клієнта..."
        required
      />
      <FormSelect
        label="Товар"
        name="product"
        value={formData.product}
        onChange={handleChange}
        options={productOptions}
        required
      />
      <FormInput
        label="Кількість"
        name="quantity"
        type="number"
        value={formData.quantity}
        onChange={handleChange}
        placeholder="1"
        required
      />
      <FormInput
        label="Дата доставки"
        name="deliveryDate"
        type="date"
        value={formData.deliveryDate}
        onChange={handleChange}
        required
      />
      <FormInput
        label="Адреса доставки"
        name="address"
        value={formData.address}
        onChange={handleChange}
        placeholder="Введіть адресу..."
        required
      />
    </FormWrapper>
  );
};