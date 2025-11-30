import React from "react";
import { categoryMap } from "../../utils/dataMap";

interface Product {
  id: number | string;
  name: string;
  category: string;
  price: number;
}

interface ProductCardProps {
  product: Product;
  onClick: (product: Product) => void;
}

export const ProductCard: React.FC<ProductCardProps> = ({
  product,
  onClick,
}) => {

  return (
    <div
      onClick={() => onClick(product)}
      className="bg-white rounded-2xl p-5 shadow-sm cursor-pointer hover:shadow-md transition-shadow"
    >
      <h3 className="text-lg font-semibold mb-1">
        {categoryMap[product.category]} "{product.name}"
      </h3>
      <p className="text-sm text-gray-500 mb-3">
        Категорія: {categoryMap[product.category]}
      </p>
      <p className="text-2xl font-bold text-indigo-600">₴{product.price}</p>
    </div>
  );
};
