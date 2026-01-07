import { useState, useEffect } from "react";
import { useCategories } from "./useCategories";

interface UseCategoriesFormOptions {
  initialCategory?: string;
}

export const useCategoriesForm = (options?: UseCategoriesFormOptions) => {
  const [selectedCategory, setSelectedCategory] = useState(
    options?.initialCategory || ""
  );
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

  // Update selectedCategory if initialCategory changes
  useEffect(() => {
    if (
      options?.initialCategory &&
      options.initialCategory !== selectedCategory
    ) {
      setSelectedCategory(options.initialCategory);
    }
  }, [options?.initialCategory]);

  // Transform categories for the select component
  const categoryOptions = categories.map((cat) => ({
    value: cat.category_id,
    label: cat.name,
  }));

  // Transform categories for the management modal
  const transformedCategories = categories.map((cat) => ({
    category_id: cat.category_id,
    name: cat.name,
    emoji: "📁",
  }));

  const handleAddCategory = async (name: string) => {
    try {
      const newCategoryId = await addCategory(name); // Returns UUID

      if (newCategoryId) {
        // Refresh categories to get the full list including the new one
        await fetchCategories();

        // Select the newly created category
        setSelectedCategory(newCategoryId);
        setIsCategoryModalOpen(false);
      }
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
      // Clear selection if deleted category was selected
      if (selectedCategory === id) {
        setSelectedCategory("");
      }
    } catch (error) {
      console.error("Failed to delete category:", error);
    }
  };

  return {
    loading,
    selectedCategory,
    setSelectedCategory,
    categoryOptions,
    isCategoryModalOpen,
    setIsCategoryModalOpen,
    transformedCategories,
    handleAddCategory,
    handleUpdateCategory,
    handleDeleteCategory,
  };
};
