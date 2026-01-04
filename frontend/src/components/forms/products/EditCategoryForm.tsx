import { useState, useEffect } from "react";
import { DynamicFormSelect } from "../../shared/DyncamicFormSelect";
import { CategoryManagementModal } from "../../features/addCategoryComponent";
import { useCategories } from "../../../hooks/products/useCategories";

export const CategoriesForm = () => {
  const [selectedCategory, setSelectedCategory] = useState("");
  const [isCategoryModalOpen, setIsCategoryModalOpen] = useState(false);

  const {
    categories,
    loading,
    fetchCategories,
    addCategory,
    updateCategory,
    deleteCategory,
    isLoaded,
  } = useCategories();

  // Fetch categories on mount
  useEffect(() => {
    if (!isLoaded) {
      fetchCategories();
    }
  }, [isLoaded, fetchCategories]);

  // Transform categories for the select component
  const categoryOptions = categories.map((cat) => ({
    value: cat.category_id,
    label: cat.name,
  }));

  // Transform categories for the management modal
  const transformedCategories = categories.map((cat) => ({
    id: cat.category_id,
    name: cat.name,
    productCount: cat.product_count || 0,
    emoji: "📁",
  }));

  const handleAddCategory = async (name: string) => {
    try {
      const newCategory = await addCategory(name);
      // Automatically select the newly created category
      setSelectedCategory(newCategory.category_id);
    } catch (error) {
      console.error("Failed to add category:", error);
    }
  };

  const handleUpdateCategory = async (id: string, name: string) => {
    try {
      await updateCategory(id, name);
    } catch (error) {
      console.error("Failed to update category:", error);
    }
  };

  const handleDeleteCategory = async (id: string) => {
    try {
      await deleteCategory(id);
      if (selectedCategory === id) {
        setSelectedCategory("");
      }
    } catch (error) {
      console.error("Failed to delete category:", error);
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Додати товар</h1>

      <form className="space-y-4">
        {/* Other form fields... */}

        <DynamicFormSelect
          label="Категорія"
          name="category"
          value={selectedCategory}
          onChange={setSelectedCategory}
          options={categoryOptions}
          required
          onAddCategory={() => setIsCategoryModalOpen(true)}
        />

        {loading && (
          <div className="text-sm text-gray-500">Завантаження категорій...</div>
        )}

        <button
          type="submit"
          className="w-full px-4 py-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition-colors"
        >
          Зберегти товар
        </button>
      </form>

      {/* Category Management Modal */}
      <CategoryManagementModal
        isOpen={isCategoryModalOpen}
        onClose={() => setIsCategoryModalOpen(false)}
        categories={transformedCategories}
        onAddCategory={handleAddCategory}
        onUpdateCategory={handleUpdateCategory}
        onDeleteCategory={handleDeleteCategory}
      />
    </div>
  );
};
