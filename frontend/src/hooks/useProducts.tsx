import { useState } from "react";
import {
  createNewProduct,
  getAllProducts,
  deleteProductById,
  updateExistingProductById,
} from "../services/api/productApi";

export const useProducts = () => {
  const [products, setProducts] = useState<Array<any>>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const addProduct = async (name: string, price: number, category: string) => {
    setLoading(true);
    setError(null);
    try {
      const newProduct = await createNewProduct(name, price, category);
      setProducts((prevProducts) => [...prevProducts, newProduct]);
    } catch (err) {
      setError("Не вдалося додати товар.");
    }
    setLoading(false);
  };

  const getProducts = async () => {
    setLoading(true);
    setError(null);
    try {
      const fetchedProducts = await getAllProducts("", 100, 0, "ASC");
      setProducts(fetchedProducts);
    } catch (err) {
      setError("Не вдалося завантажити товари.");
    }
    setLoading(false);
  };

  const deleteProduct = async (productId: string) => {
    setLoading(true);
    setError(null);
    try {
      await deleteProductById(productId);
    } catch (err) {
      setError("Не вдалося видалити товар.");
    }
    setLoading(false);
  };

  const updateProduct = async (
    productId: string,
    name: string,
    price: number,
    category: string
  ) => {
    setLoading(true);
    setError(null);
    try {
      const updatedProduct = await updateExistingProductById(
        productId,
        name,
        price,
        category
      );

      setProducts((prevProducts) =>
        prevProducts.map((product) =>
          product.id === productId ? updatedProduct : product
        )
      );
    } catch (err) {
      setError("Не вдалося оновити товар.");
    }
  };

  return {
    products,
    addProduct,
    getProducts,
    deleteProduct,
    updateProduct,
    error,
    loading,
  };
};
