import { useState, useCallback } from "react";
import {
  createNewProduct,
  getAllProducts,
  getProductSummary,
  deleteProductById,
  updateExistingProductById,
  type ProductSummary,
} from "../../services/api/productApi";
import { type Product } from "../../types/entities/Product";

const PAGE_SIZE = 20;

const getCreatedProductId = (value: unknown): string | undefined => {
  if (typeof value === "string") {
    return value;
  }

  if (value && typeof value === "object" && "product_id" in value) {
    const productId = (value as { product_id?: unknown }).product_id;
    return typeof productId === "string" ? productId : undefined;
  }

  return undefined;
};

export const useProducts = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [loadingMore, setLoadingMore] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState<boolean>(true);
  const [offset, setOffset] = useState<number>(0);
  const [currentSearch, setCurrentSearch] = useState<string>("");
  const [currentCategoryId, setCurrentCategoryId] = useState<string>("all");
  const [summary, setSummary] = useState<ProductSummary>({
    total_count: 0,
    category_counts: [],
  });

  const addProduct = async (name: string, price: number, category?: string) => {
    setLoading(true);
    setError(null);
    try {
      const createdProduct = await createNewProduct(name, price, category);
      return getCreatedProductId(createdProduct);
    } catch (error) {
      setError("Не вдалося додати товар.");
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const getProducts = async (search: string = "", categoryId = "all") => {
    setLoading(true);
    setError(null);
    setCurrentSearch(search);
    setCurrentCategoryId(categoryId);
    setOffset(0);
    try {
      const [fetchedProducts, fetchedSummary] = await Promise.all([
        getAllProducts(search, PAGE_SIZE, 0, "ASC", categoryId) as Promise<Product[]>,
        getProductSummary(search),
      ]);
      setProducts(fetchedProducts);
      setSummary(fetchedSummary);
      setHasMore(fetchedProducts.length >= PAGE_SIZE);
      setOffset(PAGE_SIZE);
      return fetchedProducts;
    } catch {
      setError("Не вдалося завантажити товари.");
      return [];
    } finally {
      setLoading(false);
    }
  };

  const loadMoreProducts = useCallback(async () => {
    if (loadingMore || loading || !hasMore) return;

    setLoadingMore(true);
    try {
      const fetchedProducts = await getAllProducts(
        currentSearch,
        PAGE_SIZE,
        offset,
        "ASC",
        currentCategoryId,
      );
      setProducts((prev) => [...prev, ...fetchedProducts]);
      setHasMore(fetchedProducts.length >= PAGE_SIZE);
      setOffset((prev) => prev + PAGE_SIZE);
    } catch {
      setError("Не вдалося завантажити більше товарів.");
    } finally {
      setLoadingMore(false);
    }
  }, [loadingMore, loading, hasMore, offset, currentSearch, currentCategoryId]);

  const deleteProduct = async (productId: string) => {
    setLoading(true);
    setError(null);
    try {
      await deleteProductById(productId);
    } catch {
      setError("Не вдалося видалити товар.");
    }
    setLoading(false);
  };

  const updateProduct = async (
    productId: string,
    name: string,
    price: number,
    category: string,
  ) => {
    setLoading(true);
    setError(null);
    try {
      const updatedProduct = await updateExistingProductById(productId, name, price, category);

      setProducts((prevProducts) =>
        prevProducts.map((product) =>
          product.product_id === productId ? updatedProduct : product,
        ),
      );
    } catch {
      setError("Не вдалося оновити товар.");
    } finally {
      setLoading(false);
    }
  };

  return {
    products,
    summary,
    addProduct,
    getProducts,
    loadMoreProducts,
    deleteProduct,
    updateProduct,
    error,
    loading,
    loadingMore,
    hasMore,
  };
};
