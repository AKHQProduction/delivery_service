import api from "../../config/api.config";

export const createNewProduct = async (
  productName: string,
  productPrice: number,
  productCategory?: string,
) => {
  const response = await api.post(`v1/products`, {
    name: productName,
    price: productPrice,
    category_id: productCategory,
  });
  return response.data;
};

export const updateExistingProductById = async (
  productId: string,
  name: string,
  price: number,
  category_id: string,
) => {
  const response = await api.patch(`v1/products/${productId}`, {
    name,
    price,
    category_id,
  });
  return response.data;
};

export const deleteProductById = async (productId: string) => {
  const response = await api.delete(`v1/products/${productId}`);
  return response.data;
};

export const getProductById = async (productId: string) => {
  const response = await api.get(`v1/products/${productId}`);
  return response.data;
};

export const getAllProducts = async (
  productName: string,
  productLimit: number,
  offset: number,
  order: string,
) => {
  const params: Record<string, string | number> = {
    limit: productLimit,
    offset: offset,
    order: order,
  };

  if (productName) params.name = productName;

  const response = await api.get(`v1/products/all`, { params });
  return response.data;
};

export const createCategory = async (categoryName: string) => {
  const response = await api.post(`v1/categories`, {
    name: categoryName,
  });
  return response.data;
};

export const updateExistingCategoryById = async (category_id: string, name: string) => {
  const response = await api.patch(`v1/categories/${category_id}`, {
    name,
  });
  return response.data;
};

export const deleteCategoryById = async (category_id: string) => {
  const response = await api.delete(`v1/categories/${category_id}`);
  return response.data;
};

export const getAllCategories = async (
  categoryName: string,
  categoryLimit: number,
  offset: number,
  order: string,
) => {
  const params: Record<string, string | number> = {
    name: categoryName,
    limit: categoryLimit,
    offset: offset,
    order: order,
  };

  if (categoryName) params.name = categoryName;
  const response = await api.get(`v1/categories/all`, { params });
  return response.data;
};
