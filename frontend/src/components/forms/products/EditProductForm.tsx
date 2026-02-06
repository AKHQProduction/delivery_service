import React, { useState, useEffect } from "react";
import { FormWrapper } from "../../shared/FormWrapper";
import { FormInput } from "../../shared/FormInput";
import { type Product } from "../../../types/entities/Product";
import { DynamicFormSelect } from "../../shared/DynamicFormSelect";
import { useCategoriesForm } from "../../../hooks/products/useCategoriesForm";
import { CategoryManagementModal } from "../../features/AddCategoryComponent";

interface EditProductFormProps {
  product: Product;
  onClose: () => void;
  onSave: (updatedProduct: Product) => Promise<void> | void;
}

export const EditProductForm: React.FC<EditProductFormProps> = ({
  product,
  onClose,
  onSave,
}) => {
  const {
    loading,
    selectedCategory,
    setSelectedCategory,
    categoryOptions,
    setIsCategoryModalOpen,
    isCategoryModalOpen,
    transformedCategories,
    handleAddCategory,
    handleUpdateCategory,
    handleDeleteCategory,
  } = useCategoriesForm(product.category_id);

  const [formData, setFormData] = useState({
    name: product.name,
    price: product.price.toString(),
  });

  // Sync selected category when product changes
  useEffect(() => {
    // If product has no category, set to "EMPTY"
    if (product.category_id && product.category_id !== "EMPTY") {
      setSelectedCategory(product.category_id);
    } else {
      setSelectedCategory("EMPTY");
    }
  }, [product.category_id, setSelectedCategory]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const updatedProduct: Product = {
      ...product,
      name: formData.name,
      price: parseFloat(formData.price),
      // Send "EMPTY" if no category is selected, otherwise send the category_id
      category_id: selectedCategory || "EMPTY",
    };

    console.log("Submitting product:", updatedProduct);
    onSave(updatedProduct);
  };

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
      
      <DynamicFormSelect
        label="Категорія"
        name="category"
        value={selectedCategory}
        onChange={setSelectedCategory}
        options={categoryOptions}
        required={false}
        onAddCategory={() => setIsCategoryModalOpen(true)}
      />

      {loading && (
        <div className="text-sm text-gray-500">Завантаження категорій...</div>
      )}

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