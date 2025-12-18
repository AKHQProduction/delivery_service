import React, { useState } from "react";
import { FormWrapper } from "../../shared/FormWrapper";
import { FormInput } from "../../shared/FormInput";
import { FormSelect } from "../../shared/FormSelect";
import { useProducts } from "../../../hooks/useProducts";

interface AddProductFormProps {
  onClose: () => void;
}

export const AddProductForm: React.FC<AddProductFormProps> = ({ onClose }) => {
  const { addProduct } = useProducts();

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    await addProduct(
      formData.name,
      parseFloat(formData.price),
      formData.category
    );
    window.location.reload(); //TEMPORARY SOLUTION
    onClose();
  };

  const categoryOptions = [
    { value: "WATER", label: "Вода" },
    { value: "OTHER", label: "Інше" },
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
        onChange={(value) =>
          setFormData((prev) => ({ ...prev, category: value }))
        }
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
