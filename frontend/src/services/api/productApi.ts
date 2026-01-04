import api from "../../config/api.config";

export const createNewProduct = async (
  productName: string,
  productPrice: number,
  productCategory: string
) => {
  try {
    const response = await api.post(`v1/products`, {
      name: productName,
      price: productPrice,
      category: productCategory,
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const updateExistingProductById = async (
  productId: string,
  name: string,
  price: number,
  category_id: string
) => {
  try {
    const response = await api.patch(`v1/products/${productId}`, {
      name,
      price,
      category_id,
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const deleteProductById = async (productId: string) => {
  try {
    const response = await api.delete(`v1/products/${productId}`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const getProductById = async (productId: string) => {
  try {
    const response = await api.get(`v1/products/${productId}`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const getAllProducts = async (
  productName: string,
  productLimit: number,
  offset: number,
  order: string
) => {
  try {
    const params: Record<string, string | number> = {
      limit: productLimit,
      offset: offset,
      order: order,
    };

    if (productName) params.name = productName;

    const response = await api.get(`v1/products/all`, { params });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const createCategory = async (categoryName: string) => {
  try {
    const response = await api.post(`v1/categories`, {
      name: categoryName,
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const updateExistingCategoryById = async (
  category_id: string,
  name: string
) => {
  try {
    const response = await api.patch(`v1/categories/${category_id}`, {
      name,
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const deleteCategoryById = async (category_id: string) => {
  try {
    const response = await api.delete(`v1/categories/${category_id}`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const getAllCategories = async (
  categoryName: string,
  categoryLimit: number,
  offset: number,
  order: string
) => {
  try {
    const params: Record<string, string | number> = {
      name: categoryName,
      limit: categoryLimit,
      offset: offset,
      order: order,
    };

    if (categoryName) params.name = categoryName;
    const response = await api.get(`v1/categories/all`, { params });
    return response.data;
  } catch (error) {
    throw error;
  }
};
