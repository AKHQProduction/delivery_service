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

const isCategory = (value: unknown): value is Category => {
  if (!value || typeof value !== "object") return false;

  const category = value as Partial<Category>;
  return typeof category.category_id === "string" && typeof category.name === "string";
};

const normalizeCategories = (value: unknown): Category[] => {
  if (!Array.isArray(value)) return [];
  return value.filter(isCategory);
};

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
      order: string = "ASC",
    ) => {
      setLoading(true);
      setError(null);
      try {
        const response = await getAllCategories(searchName, limit, offset, order);
        const fetchedCategories = normalizeCategories(response.categories || response);
        setCategories(fetchedCategories);
        hasFetchedRef.current = true;
        console.log("Fetched categories:", fetchedCategories);
        return fetchedCategories;
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : "Failed to fetch categories";
        setError(message);
        console.error("Error fetching categories:", err);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [],
  );

  const addCategory = useCallback(
    async (name: string) => {
      setError(null);
      try {
        const newCategory = await createCategory(name);
        if (isCategory(newCategory)) {
          setCategories((prev) => [...prev, newCategory]);
        } else if (hasFetchedRef.current) {
          await fetchCategories();
        }
        return newCategory;
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : "Failed to create category";
        setError(message);
        console.error("Error creating category:", err);
        // Revert on error by refetching
        if (hasFetchedRef.current) {
          fetchCategories();
        }
        throw err;
      }
    },
    [fetchCategories],
  );

  const updateCategory = useCallback(
    async (categoryId: string, name: string) => {
      setError(null);

      // Store previous state for rollback
      const previousCategories = categories;

      // Optimistically update
      setCategories((prev) =>
        prev.map((cat) => (cat.category_id === categoryId ? { ...cat, name } : cat)),
      );

      try {
        const updatedCategory = await updateExistingCategoryById(categoryId, name);
        return updatedCategory;
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : "Failed to update category";
        setError(message);
        console.error("Error updating category:", err);
        // Rollback on error
        setCategories(previousCategories);
        throw err;
      }
    },
    [categories],
  );

  const deleteCategory = useCallback(
    async (categoryId: string) => {
      setError(null);

      // Store previous state for rollback
      const previousCategories = categories;

      // Optimistically update
      setCategories((prev) => prev.filter((cat) => cat.category_id !== categoryId));

      try {
        await deleteCategoryById(categoryId);
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : "Failed to delete category";
        setError(message);
        console.error("Error deleting category:", err);
        // Rollback on error
        setCategories(previousCategories);
        throw err;
      }
    },
    [categories],
  );

  // Helper to check if categories are loaded
  const isLoaded = hasFetchedRef.current;

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
