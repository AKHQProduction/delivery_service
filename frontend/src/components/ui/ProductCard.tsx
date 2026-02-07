import React from "react";
import { type Product } from "../../types/entities/Product";

interface ProductCardProps {
  product: Product;
  onClick: (product: Product) => void;
}

export const ProductCard: React.FC<ProductCardProps> = ({ product, onClick }) => {
  return (
    <div
      onClick={() => onClick(product)}
      className="bg-white rounded-2xl p-5 shadow-sm cursor-pointer border border-gray-100 hover:shadow-2xl hover:-translate-y-2 transition-all duration-300"
    >
      <h3 className="text-lg font-semibold mb-1">{product.name}</h3>
      <p className="text-sm text-gray-500 mb-3">
        Категорія: {product.category_name || "Без категорії"}
      </p>
      <p className="text-2xl font-bold text-indigo-600">₴{product.price}</p>
    </div>
  );
};
