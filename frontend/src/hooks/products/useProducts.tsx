import { useState, useCallback } from "react";
import {
  createNewProduct,
  getAllProducts,
  deleteProductById,
  updateExistingProductById,
} from "../../services/api/productApi";
import { type Product } from "../../types/entities/Product";

const PAGE_SIZE = 20;

export const useProducts = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [loadingMore, setLoadingMore] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState<boolean>(true);
  const [offset, setOffset] = useState<number>(0);
  const [currentSearch, setCurrentSearch] = useState<string>("");

  const addProduct = async (name: string, price: number, category?: string) => {
    setLoading(true);
    setError(null);
    try {
      const newProduct = (await createNewProduct(name, price, category)) as Product;
      setProducts((prevProducts) => [newProduct, ...prevProducts]);
      return newProduct;
    } catch (error) {
      setError("Не вдалося додати товар.");
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const getProducts = async (search: string = "") => {
    setLoading(true);
    setError(null);
    setCurrentSearch(search);
    setOffset(0);
    try {
      const fetchedProducts = (await getAllProducts(search, PAGE_SIZE, 0, "ASC")) as Product[];
      setProducts(fetchedProducts);
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
    if (loadingMore || !hasMore) return;

    setLoadingMore(true);
    try {
      const fetchedProducts = await getAllProducts(currentSearch, PAGE_SIZE, offset, "ASC");
      setProducts((prev) => [...prev, ...fetchedProducts]);
      setHasMore(fetchedProducts.length >= PAGE_SIZE);
      setOffset((prev) => prev + PAGE_SIZE);
    } catch {
      setError("Не вдалося завантажити більше товарів.");
    } finally {
      setLoadingMore(false);
    }
  }, [loadingMore, hasMore, offset, currentSearch]);

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
    }
  };

  return {
    products,
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
