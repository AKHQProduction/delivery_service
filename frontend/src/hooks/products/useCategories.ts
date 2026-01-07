import { useState, useCallback, useRef } from "react";
import {
  createCategory,
  updateExistingCategoryById,
  deleteCategoryById,
  getAllCategories,
} from "../../services/api/productApi";

interface Category {
  category_id: string;
  name: string;
  product_count?: number;
}

export const useCategories = () => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Track if categories have been fetched to prevent duplicate initial loads
  const hasFetchedRef = useRef(false);

  const fetchCategories = useCallback(
    async (
      searchName: string = "",
      limit: number = 100,
      offset: number = 0,
      order: string = "ASC"
    ) => {
      setLoading(true);
      setError(null);
      try {
        const response = await getAllCategories(
          searchName,
          limit,
          offset,
          order
        );
        const fetchedCategories = response.categories || response;
        setCategories(fetchedCategories);
        hasFetchedRef.current = true;
        console.log("Fetched categories:", fetchedCategories);
        return fetchedCategories;
      } catch (err: any) {
        setError(err.message || "Failed to fetch categories");
        console.error("Error fetching categories:", err);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const addCategory = useCallback(
    async (name: string) => {
      setError(null);
      try {
        const newCategory = await createCategory(name);
        // Optimistically update the state
        setCategories((prev) => [...prev, newCategory]);
        return newCategory;
      } catch (err: any) {
        setError(err.message || "Failed to create category");
        console.error("Error creating category:", err);
        // Revert on error by refetching
        if (hasFetchedRef.current) {
          fetchCategories();
        }
        throw err;
      }
    },
    [fetchCategories]
  );

  const updateCategory = useCallback(
    async (categoryId: string, name: string) => {
      setError(null);
      
      // Store previous state for rollback
      const previousCategories = categories;
      
      // Optimistically update
      setCategories((prev) =>
        prev.map((cat) =>
          cat.category_id === categoryId ? { ...cat, name } : cat
        )
      );

      try {
        const updatedCategory = await updateExistingCategoryById(
          categoryId,
          name
        );
        return updatedCategory;
      } catch (err: any) {
        setError(err.message || "Failed to update category");
        console.error("Error updating category:", err);
        // Rollback on error
        setCategories(previousCategories);
        throw err;
      }
    },
    [categories]
  );

  const deleteCategory = useCallback(
    async (categoryId: string) => {
      setError(null);
      
      // Store previous state for rollback
      const previousCategories = categories;
      
      // Optimistically update
      setCategories((prev) =>
        prev.filter((cat) => cat.category_id !== categoryId)
      );

      try {
        await deleteCategoryById(categoryId);
      } catch (err: any) {
        setError(err.message || "Failed to delete category");
        console.error("Error deleting category:", err);
        // Rollback on error
        setCategories(previousCategories);
        throw err;
      }
    },
    [categories]
  );

  // Helper to check if categories are loaded
  const isLoaded = hasFetchedRef.current

  return {
    categories,
    loading,
    error,
    isLoaded,
    fetchCategories,
    addCategory,
    updateCategory,
    deleteCategory,
  };
};