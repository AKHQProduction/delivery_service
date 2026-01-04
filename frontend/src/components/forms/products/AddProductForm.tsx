import React, { useState } from "react";
import { FormWrapper } from "../../shared/FormWrapper";
import { FormInput } from "../../shared/FormInput";
import { useProducts } from "../../../hooks/products/useProducts";
import { DynamicFormSelect } from "../../shared/DyncamicFormSelect";
import { useCategoriesForm } from "../../../hooks/products/useCategoriesForm";
import { CategoryManagementModal } from "../../features/addCategoryComponent";
import { type Product } from "../../../types/entities/Product";

interface AddProductFormProps {
  onClose: () => void;
  onSuccess?: (product: Product) => void;
}

export const AddProductForm: React.FC<AddProductFormProps> = ({
  onClose,
  onSuccess,
}) => {
  // Pass initial category to the hook
  const {
    selectedCategory,
    setSelectedCategory,
    categoryOptions,
    setIsCategoryModalOpen,
    isCategoryModalOpen,
    transformedCategories,
    handleAddCategory,
    handleUpdateCategory,
    handleDeleteCategory,
  } = useCategoriesForm();

  const { addProduct } = useProducts();

  const [formData, setFormData] = useState({
    name: "",
    price: "",
  });

  const category =
    selectedCategory && selectedCategory.trim() !== ""
      ? selectedCategory
      : undefined;

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const newProduct = await addProduct(
        formData.name,
        parseFloat(formData.price),
        category
      );
      if (onSuccess && newProduct) {
        onSuccess(newProduct);
      }

      onClose();
    } catch (error) {
      console.error("Error creating product:", error);
    }
  };

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
      <DynamicFormSelect
        label="Категорія"
        name="category"
        value={selectedCategory}
        onChange={setSelectedCategory}
        options={categoryOptions}
        onAddCategory={() => setIsCategoryModalOpen(true)}
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
      <CategoryManagementModal
        isOpen={isCategoryModalOpen}
        onClose={() => setIsCategoryModalOpen(false)}
        categories={transformedCategories}
        onAddCategory={handleAddCategory}
        onUpdateCategory={handleUpdateCategory}
        onDeleteCategory={handleDeleteCategory}
      />
    </FormWrapper>
  );
};
