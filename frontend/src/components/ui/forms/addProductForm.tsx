import React, { useState } from "react";
import { FormWrapper } from "./formWrapper";
import { FormInput } from "./formInput";
import { FormSelect } from "./formSelect";

interface AddProductFormProps {
  onClose: () => void;
}

export const AddProductForm: React.FC<AddProductFormProps> = ({ onClose }) => {
  const [formData, setFormData] = useState({
    name: "",
    category: "",
    price: "",
  });

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Product submitted:", formData);
    // Add your API call here
    onClose();
  };

  const categoryOptions = [
    { value: "Вода", label: "Вода" },
    { value: "Інше", label: "Інше" },
  ];

  return (
    <FormWrapper
      onSubmit={handleSubmit}
      onClose={onClose}
      submitLabel="Додати товар"
    >
      <FormInput
        label="Назва товару"
        name="name"
        value={formData.name}
        onChange={handleChange}
        placeholder="Введіть назву..."
        required
      />
      <FormSelect
        label="Категорія"
        name="category"
        value={formData.category}
        onChange={handleChange}
        options={categoryOptions}
        required
      />
      <FormInput
        label="Ціна (₴)"
        name="price"
        type="number"
        value={formData.price}
        onChange={handleChange}
        placeholder="0"
        required
      />
    </FormWrapper>
  );
};
