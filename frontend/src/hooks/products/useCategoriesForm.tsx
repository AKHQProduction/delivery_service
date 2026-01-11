import { useState, useEffect } from "react";
import { useCategories } from "./useCategories";

export const useCategoriesForm = (initialCategoryId?: string | null) => {
  const {
    categories,
    fetchCategories,
    addCategory,
    updateCategory,
    deleteCategory,
  } = useCategories();

  const [loading, setLoading] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(
    initialCategoryId || "EMPTY"
  );
  const [isCategoryModalOpen, setIsCategoryModalOpen] = useState(false);

  useEffect(() => {
    const loadCategories = async () => {
      setLoading(true);
      await fetchCategories();
      setLoading(false);
    };
    loadCategories();
  }, []);

  // Create category options with "No Category" as first option using "EMPTY" value
  const categoryOptions = [
    {
      value: "EMPTY",
      label: "Без категорії",
    },
    ...categories.map((cat) => ({
      value: cat.category_id,
      label: `${cat.name}`,
    })),
  ];

  // Transform categories for management modal (excluding "No Category")
  const transformedCategories = categories.map((cat) => ({
    id: cat.category_id,
    name: cat.name,
    emoji: "📁",
  }));

  const handleAddCategory = async (name: string) => {
    try {
      await addCategory(name);
      await fetchCategories();
    } catch (error) {
      console.error("Failed to add category:", error);
      throw error;
    }
  };

  const handleUpdateCategory = async (id: string, name: string) => {
    try {
      await updateCategory(id, name);
      await fetchCategories();
    } catch (error) {
      console.error("Failed to update category:", error);
      throw error;
    }
  };

  const handleDeleteCategory = async (id: string) => {
    try {
      await deleteCategory(id);
      await fetchCategories();
      // If the deleted category was selected, reset to "EMPTY"
      if (selectedCategory === id) {
        setSelectedCategory("EMPTY");
      }
    } catch (error) {
      console.error("Failed to delete category:", error);
      throw error;
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