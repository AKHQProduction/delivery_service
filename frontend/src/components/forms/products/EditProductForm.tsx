import React, { useState } from "react";
import { FormWrapper } from "../shared/FormWrapper";
import { FormInput } from "../shared/FormInput";
import { FormSelect } from "../shared/FormSelect";
import { type Product } from "../../../types/entities/Product";

interface EditProductFormProps {
  product: Product;
  onClose: () => void;
  onSave: (updatedProduct: Product) => void;
}

export const EditProductForm: React.FC<EditProductFormProps> = ({
  product,
  onClose,
  onSave,
}) => {
  const [formData, setFormData] = useState({
    name: product.name,
    category: product.category,
    price: product.price.toString(),
  });

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const updatedProduct: Product = {
      product_id: product.product_id,
      name: formData.name,
      category: formData.category,
      price: parseFloat(formData.price),
    };

    onSave(updatedProduct);
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
      submitLabel="Зберегти зміни"
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
